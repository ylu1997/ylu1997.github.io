# DIMON 方法核心流程梳理
## 总体思路

> **Remark**：从整体上看，DIMON 的核心贡献在于：用**配准**（registration）来实现几何信息的提取与编码。配准建立了各域与参考域之间的点对应关系，由此同时完成两件事：一是将几何形状压缩为低维参数 $\tilde{\theta}$，二是将不同域上的函数统一搬运到同一参考域（定义域）。神经算子的学习完全在参考域上进行，几何变化对网络而言只是一个额外的输入参数。

## 问题设定

设有一族有界开域 $\{\Omega_\theta\}_{\theta \in \Theta}$，$\Theta \subset \mathbb{R}^p$ 为紧集。对每个 $\theta$，PDE 确定一个解算子：

$$\mathcal{G}_\theta : X_1(\Omega_\theta) \times \cdots \times X_m(\Omega_\theta) \to Y(\Omega_\theta)$$

将边界/初始条件 $v^\theta$ 映射到解 $u^\theta$。困难在于：不同 $\theta$ 对应的函数空间各不相同，无法直接统一学习。

**目标**：在一族微分同胚等价的域上，训练单一模型快速预测 PDE 解，替代逐域数值求解。

## 核心概念

### 微分同胚与拉回

假设每个 $\Omega_\theta$ 均与固定参考域 $\Omega_0$ 微分同胚，存在 $\mathcal{C}^2$ 微分同胚 $\varphi_\theta : \Omega_0 \xrightarrow{\sim} \Omega_\theta$。

利用**拉回** $\varphi_\theta^* f := f \circ \varphi_\theta$，将 $\Omega_\theta$ 上的函数搬运到 $\Omega_0$：

$$v^0_\theta = v^\theta \circ \varphi_\theta, \quad u^0_\theta = u^\theta \circ \varphi_\theta$$

对于**标量函数**，拉回即为复合 $f \circ \varphi_\theta$。对于**向量场** $v : \Omega_0 \to \mathbb{R}^d$，$\varphi_\theta$ 的作用需通过 Jacobian 矩阵：

$$(\varphi_\theta)_* v(x) = J_{\varphi_\theta}(x) \cdot v(x)$$

其中 $J_{\varphi_\theta}$ 为 $\varphi_\theta$ 的 Jacobian 矩阵。协变/逆变张量场有对应的推广形式。

从而将各域上不同的函数空间统一为 $\Omega_0$ 上的单一空间。

### 潜在算子 $\mathcal{F}_0$

通过拉回，解算子族 $\{\mathcal{G}_\theta\}$ 等价表示为参考域上的单一潜在算子：

$$\mathcal{G}_\theta(v^\theta) = \mathcal{F}_0\!\left(\theta,\ \varphi_\theta^* v^\theta\right) \circ \varphi_\theta^{-1}$$

> **Remark**：$\mathcal{G}_\theta$ 对应 Eulerian 视角（解定义在变化的域上），$\mathcal{F}_0$ 对应 Lagrangian 视角（固定参考域，形变编码在参数 $\theta$ 里）。$\mathcal{F}_0$ 也可理解为：将原始 PDE 通过 $\varphi_\theta$ 做变量替换后，定义在 $\Omega_0$ 上的参数化 PDE 的解算子。

### 概念关系总览

```
几何族 {Ω_θ}（有限元网格）
    │  传统配准（LDDMM / 解析参数化 / UVC）
    ▼
微分同胚 φ_θ：Ω_0 节点 → Ω_θ 中对应位置（分片线性插值读值）
    │  PCA 降维（位移向量标准 PCA 或 LDDMM 动量测地线 PCA）
    ▼
形状参数 θ̃ ∈ ℝ^{p'}
    │
    ├── 拉回：v^θ 插值重采样到 Ω_0 节点 → v^0_θ
    │
    └── MIONet 学习 F_0(θ̃, v^0_θ) = u^0_θ
            │  φ_θ^{-1} 插值推回
            ▼
        原始域解 û^θ
```

## 数据对象与离散化

### 网格结构

底层数据对象为**非结构化单纯形 FEM 网格**上的离散函数值，插值方式为分片线性（$P_1$ FEM）。

- 空间被离散为一组**采样节点**（坐标数组）及其上的**单纯形剖分信息**（二维为三角形，三维为四面体），二者共同构成网格。
- $\varphi_\theta$ 在计算上的实现：给定查询点，定位其所在单纯形，用**重心坐标做线性插值**得到映射值。这是对理论上 $\mathcal{C}^2$ 微分同胚的分片线性近似——连续但不光滑。
- $\Omega_0$ 与各 $\Omega_\theta$ 的节点数目和单纯形拓扑可以各不相同。

> **Remark**：节点坐标数组可以理解为对空间的采样，单纯形剖分信息记录了哪些采样点构成一个单元。两者合在一起才能支持插值操作。"通过三角剖分实现微分同胚"的准确表述是：在单纯形剖分上做分片线性插值，作为理论微分同胚的计算近似。文章在理论层面要求 $\varphi_\theta \in \mathcal{C}^2$，但计算实现中实际使用的是分片线性映射，后者仅在单纯形内部光滑，跨单元界面处只有 $C^0$ 连续性，并不满足 $\mathcal{C}^2$ 条件。这是理论假设与数值实现之间的一个 gap。

### 离散对象汇总

| 环节 | 数据对象 |
|------|----------|
| $\varphi_\theta$ 的表示 | landmark 点的位移向量 $\{x - \varphi_\theta(x)\}$ |
| 函数拉回 | $\Omega_\theta$ 节点值通过点对应插值重采样到 $\Omega_0$ 节点 |
| Branch 输入 | 离散点上的函数值向量 $\tilde{v} \in \mathbb{R}^n$ |
| Trunk 输入 | 参考域坐标 $x \in \Omega_0$（连续，逐点查询） |

> **Remark**：配准不是在原网格上插入新节点，而是找到 $\Omega_0$ 各节点在 $\Omega_\theta$ 中的对应位置，再通过插值读取该位置的函数值。插值发生在"读值"这一步，网格拓扑本身不变。

## 核心流程

### 第零步：参考域 $\Omega_0$ 的选取

$\Omega_0$ 的选取无唯一标准，实践中的策略包括：

- 选取形状简单且与所有 $\Omega_\theta$ 微分同胚等价的域（如示例1中的单位正方形、示例3中的空心半球）；
- 从数据集中选取某个 $\Omega_{\theta_i}$ 作为参考；
- 用模板估计方法从数据集中估计一个"平均形状"。

选取标准的核心约束是：$\Omega_0$ 必须与所有 $\Omega_\theta$ 微分同胚等价。

### 第一步：几何配准（离线，传统方法）

对每个 $\Omega_\theta$，计算微分同胚 $\varphi_\theta : \Omega_0 \to \Omega_\theta$，建立点对应关系。

文章使用的配准方法：

- **解析参数化**（示例1）：$\varphi_\theta$ 由显式参数方程直接给出。
- **仿射极坐标变换**（示例2）：笛卡尔坐标转极坐标并归一化，适用于规则环形域。
- **LDDMM**（示例2、3）：求解能量最小的微分同胚形变路径：

$$\inf_{v} \left\{ \int_0^1 \|v(t,\cdot)\|_V^2 \, dt \ \Big|\ \varphi_v(\Omega) = \Omega' \right\}$$

  形变由时变光滑向量场 $v(t, \cdot)$ 的流生成，是定义在全空间 $\mathbb{R}^d$ 上的全局光滑微分同胚。最优路径为测地线，可由初始动量紧凑表示。

> **Remark**：LDDMM 与图像处理中"控制点网格形变"的直觉类似，但本质不同：后者是分片仿射（锚点间线性插值），LDDMM 的形变在全空间是光滑的，由偏微分方程（流方程）而非插值公式决定。

- **UVC 配准**（示例3）：用通用心室坐标（$\rho, \delta, \phi$）对齐各患者左心室网格。

对所有 $\varphi_\theta$ 做 PCA，得低维形状参数 $\tilde{\theta} \in \mathbb{R}^{p'}$。文章使用两种 PCA 方案：

- **标准 PCA**：对 landmark 点的位移向量 $\{x - \varphi_\theta(x)\}$ 做标准 PCA；
- **测地线 PCA（Geodesic PCA）**：对 LDDMM 的动量或形变表示做测地线 PCA，利用 LDDMM 的 Riemannian 结构。

> **Remark**：文章引入 PCA 的主要动机是**可扩展性**：原始 $\varphi_\theta$ 表示维度极高，直接作为网络输入会导致训练代价剧增；在 MRI/CT 分辨率下甚至根本不可行。PCA 降维可将输入压缩到 $\mathbb{R}^{p'}$，显著降低内存和计算开销。
>
> 关于 PCA 截断对上下游的影响，文章有以下处理：
> - **对推回步骤无影响**：$\tilde{\theta}$ 仅用于网络输入，推回原始域时仍使用完整的原始映射 $\varphi_\theta$，因此 PCA 截断误差不影响最终插值推回的几何精度。
> - **对网络训练的影响**：文章在 Supplementary Section 4 中对比了使用完整 $\theta$ 与截断 $\tilde{\theta}$ 的网络性能，但正文未展开定量分析。
> - **未讨论的 gap**：保留多少个主成分最优、截断误差与最终 PDE 解误差之间的定量传播关系，以及 PCA 对高度非线性形变族的适用性，均未在文章中系统讨论。

### 第二步：函数拉回到参考域

将 $\Omega_\theta$ 上的输入函数和 PDE 解通过插值重采样到 $\Omega_0$：

$$v^0_\theta = v^\theta \circ \varphi_\theta, \quad u^0_\theta = u^\theta \circ \varphi_\theta$$

具体操作：对 $\Omega_0$ 的每个节点 $x$，计算其在 $\Omega_\theta$ 中的像 $\varphi_\theta(x)$，在 $\Omega_\theta$ 的 FEM 网格上插值读取 $v^\theta(\varphi_\theta(x))$。

### 第三步：在参考域上学习解算子（MIONet）

在固定参考域 $\Omega_0$ 上训练 MIONet（DeepONet 的多输入扩展）。输出函数在点 $x$ 处的值为：

$$\tilde{\mathcal{F}}_0(\tilde{\theta}, v^0_\theta)(x) = \mathcal{S}\!\left(\tilde{g}_0\!\left(\varphi_0^{q_0}(\tilde{\theta})\right) \odot \tilde{g}_1\!\left(\varphi_1^{q_1}(v^0_\theta)\right) \odot \cdots \odot \tilde{f}(x)\right)$$

其中 $\mathcal{S}$ 为对向量所有分量求和，$\odot$ 为 Hadamard 积，$q_i$ 为各 branch 的输出维度。等价的展开形式为：

$$\tilde{\mathcal{F}}_0(\tilde{\theta}, v_1, \ldots, v_m)(x) = \sum_{i=1}^k t_i \prod_{j=1}^m b_j^i \cdot b_{\text{geo}}^i + b$$

- **Geo. branch** $\tilde{g}_0$：输入形状参数 $\tilde{\theta}$，编码**域的几何形状**。
- **Func. branch** $\tilde{g}_1$：输入拉回到 $\Omega_0$ 上的边界条件或初始条件的离散值 $\tilde{v} = v^0_\theta|_{\text{nodes}}$，编码**本次求解的 PDE 激励**。在示例1中为边界条件（BC branch），在示例2、3中为初始条件（IC branch）。
- **Trunk** $\tilde{f}$：输入参考域坐标 $x$，逐点查询输出值。

框架对神经算子架构的选取无约束，MIONet 为默认选择，可替换为 FNO 等其他算子（plug-and-play）。

对于**时间依赖算子**，将时间 $t$ 拼接到参考域坐标 $x$ 中作为 trunk 输入，即令 trunk 输入为 $(x, t)$，无需修改框架其他部分。

> **Remark**：两个 branch 的分工：Geo. branch 回答"在哪个形状上求解"，Func. branch 回答"这次的激励条件是什么"。同一几何形状在不同边界/初始条件下会给出不同的解，因此两者缺一不可。MIONet 与 DeepONet 的区别仅在于多个 branch 并行输入，以 Hadamard 积融合，本质结构一致。

### 第四步：推回原始域

$$\hat{u}^\theta = \tilde{\mathcal{F}}_0(\tilde{\theta}, v^0_\theta) \circ \varphi_\theta^{-1}$$

## 普适逼近定理

文章将 DeepONet 的 UAT 推广至此设定：在各输入空间具有 Schauder 基、$\mathcal{F}_0$ 连续的条件下，MIONet 可以任意精度逼近 $\mathcal{F}_0$。

> **Remark**：$\mathcal{F}_0$ 关于 $\theta$ 的连续性（即解对域形变的连续依赖）在一般情形非平凡。文章对 Laplace 方程在 $\mathcal{C}^2$ 边界假设下给出了完整论证。
