# Latex Literature Management System

<!-- TOC -->

- [Latex Literature Management System](#latex-literature-management-system)
    - [What It Does](#what-it-does)
    - [Understanding the Insight Field](#understanding-the-insight-field)
        - [🆕 Recommended Inline Format](#-recommended-inline-format)
        - [Format Helpers](#format-helpers)
    - [Installation](#installation)
    - [Download](#download)
    - [BibTeX Conversion Tools](#bibtex-conversion-tools)
        - [GUI Converter ConvertGUI.py](#gui-converter-convertguipy)
        - [Core Converter BibConverter.py](#core-converter-bibconverterpy)
        - [Usage Examples](#usage-examples)
    - [Core Functions](#core-functions)
        - [Data Input](#data-input)
            - [\addliterature{title}{authors}{year}{insight}{tag}](#%5Caddliteraturetitleauthorsyearinsighttag)
            - [\addliteratureold{title}{authors}{year}{insight}](#%5Caddliteratureoldtitleauthorsyearinsight)
        - [Sorting Functions](#sorting-functions)
            - [\sortbyyear](#%5Csortbyyear)
            - [\sortbytitle](#%5Csortbytitle)
            - [\sortbyauthors](#%5Csortbyauthors)
            - [\sortbytag](#%5Csortbytag)
            - [\sortbyyeartitle](#%5Csortbyyeartitle)
            - [\sortbytagyear](#%5Csortbytagyear)
            - [\sortby{field}](#%5Csortbyfield)
        - [Display Functions](#display-functions)
            - [Standard Display Functions](#standard-display-functions)
            - [\showfullreview](#%5Cshowfullreview)
            - [\showbasiclist](#%5Cshowbasiclist)
            - [\showbasiclistwithinsight](#%5Cshowbasiclistwithinsight)
            - [🆕 Inline Format Functions](#-inline-format-functions)
            - [\showfullreviewinline](#%5Cshowfullreviewinline)
            - [\showbasiclistinline](#%5Cshowbasiclistinline)
            - [🆕 Compact Format Functions](#-compact-format-functions)
            - [\showfullreviewcompact](#%5Cshowfullreviewcompact)
            - [\showbasiclistcompact](#%5Cshowbasiclistcompact)
        - [Tag-Based Filtering](#tag-based-filtering)
            - [Standard Tag Filtering](#standard-tag-filtering)
            - [\showfullreviewbytag{tag}](#%5Cshowfullreviewbytagtag)
            - [\showbasiclistbytag{tag}](#%5Cshowbasiclistbytagtag)
            - [\showbasiclistwithinsightbytag{tag}](#%5Cshowbasiclistwithinsightbytagtag)
            - [🆕 Inline Format Tag Filtering](#-inline-format-tag-filtering)
            - [\showfullreviewbytaginline{tag}](#%5Cshowfullreviewbytaginlinetag)
            - [\showbasiclistbytaginline{tag}](#%5Cshowbasiclistbytaginlinetag)
            - [🆕 Compact Format Tag Filtering](#-compact-format-tag-filtering)
            - [\showfullreviewbytagcompact{tag}](#%5Cshowfullreviewbytagcompacttag)
            - [\showbasiclistbytagcompact{tag}](#%5Cshowbasiclistbytagcompacttag)
        - [🆕 Inline Format Helpers](#-inline-format-helpers)
            - [\inlineitem{text}](#%5Cinlineitemtext)
            - [\inlinesep](#%5Cinlinesep)
            - [\inlinearrow](#%5Cinlinearrow)
        - [Statistics and Information](#statistics-and-information)
            - [\showstats](#%5Cshowstats)
            - [\getpapercount](#%5Cgetpapercount)
            - [\showavailabletags](#%5Cshowavailabletags)
            - [\systeminfo](#%5Csysteminfo)
        - [Database Management](#database-management)
            - [\clearliterature](#%5Cclearliterature)
            - [\resetpapercount](#%5Cresetpapercount)
    - [🆕 Recommended Usage Patterns](#-recommended-usage-patterns)
        - [Best Practices for v3.0](#best-practices-for-v30)
    - [Complete Example](#complete-example)
    - [Key Features](#key-features)

<!-- /TOC -->ures](#key-features)

<!-- /TOC -->

A LaTeX system for managing academic literature with automated sorting, tag-based filtering, and multiple display formats. Built on the `datatool` package for structured data storage and processing.

## What It Does

This system allows you to:
- Store literature data in a structured database
- Sort by multiple criteria (year, title, author, tags)
- Filter by tags for topic-based organization
- Display in various formats (detailed tables, compact lists, **inline format**)
- Generate statistics and analytics
- **Convert BibTeX entries to addliterature format automatically**
- **🆕 Use inline format to solve table spacing issues**
- **🆕 Compact display for better space utilization**

## Understanding the Insight Field

**The Insight field serves as your literature reading notes**, designed to capture the essential value and your personal understanding of each paper. 

### 🆕 Recommended Inline Format

For better table display and space efficiency, use the **inline format** for insights:

```latex
% Recommended: Inline format (v3.0)
\addliterature{Attention Is All You Need}{Vaswani et al.}{2017}{
\textbf{Key Contributions:} Proposes Transformer architecture • Entirely based on attention mechanisms • Eliminates recurrence and convolution • Enables parallelizable training
}{NLP,Attention}

% Alternative: Traditional itemize format
\addliterature{BERT}{Devlin et al.}{2018}{
\item Breakthrough bidirectional encoding representations
\item Pre-training through masked language model
\item Achieves new records on 11 NLP tasks
}{NLP,BERT}
```

**Key insight recording areas:**
- **Innovative Ideas**: Novel theories, concepts, or perspectives
- **Key Methods**: Important research methods and technical approaches
- **Main Conclusions**: Core findings and significant discoveries
- **Future Directions**: Suggestions for future research
- **Personal Reflections**: Your insights and application ideas

### Format Helpers

Use these inline format helpers for consistent styling:

- `\inlineitem{1}` → **1**
- `\inlinesep` → •
- `\inlinearrow` → →

## Installation

```latex
\input{literature-system.tex}
```

## Download

📥 **Get the LaTeX system file:**

- **Direct Download**: [literature-system.tex](./literature-system.tex)
- **Raw File**: [literature-system.tex (raw)](./literature-system.tex?raw=true)

Simply download the `literature-system.tex` file and place it in your LaTeX project directory, then include it using `\input{literature-system.tex}` in your document.

## BibTeX Conversion Tools

To streamline the process of adding literature from BibTeX sources, we provide two Python-based conversion tools that automatically convert BibTeX entries to the `\addliterature` format.

### GUI Converter (ConvertGUI.py)

**🖥️ Graphical User Interface Tool**

A user-friendly desktop application with the following features:

- **Batch Processing**: Convert multiple BibTeX entries simultaneously
- **Real-time Validation**: Verify BibTeX format before conversion
- **Copy to Clipboard**: One-click copying of conversion results
- **Error Handling**: Clear error messages for problematic entries
- **Sample Data**: Pre-loaded examples for testing

**Usage:**
```bash
python ConvertGUI.py
```

**Features:**
- Drag-and-drop or paste multiple BibTeX entries
- Automatic citation key integration (`\cite{key}`)
- Batch validation and conversion
- Clean, intuitive interface
- Status tracking and progress indication

### Core Converter (BibConverter.py)

**⚙️ Python Library for Programmatic Use**

A robust Python class for BibTeX conversion with advanced features:

```python
from BibConverter import BibConverter

converter = BibConverter()

# Convert single BibTeX entry
bib_text = """@article{Vaswani2017,
title={Attention Is All You Need},
author={Ashish Vaswani and Noam Shazeer and Niki Parmar},
year={2017}
}"""

result = converter.convert_bib_to_addliterature(bib_text)
print(result)
# Output: \addliterature{Attention Is All You Need\cite{Vaswani2017}}{Ashish Vaswani and Noam Shazeer and Niki Parmar}{2017}{}{}

# Batch conversion
multiple_bibs = """@article{entry1,...}
@article{entry2,...}"""

success_results, error_messages = converter.convert_multiple_bibs(multiple_bibs)
```

**Key Methods:**
- `convert_bib_to_addliterature(bib_text)`: Convert single entry
- `convert_multiple_bibs(text)`: Batch conversion with error handling
- `validate_bib_format(bib_text)`: Format validation
- `extract_field(bib_text, field_name)`: Extract specific fields
- `get_entry_key(bib_text)`: Extract citation keys

### Usage Examples

**1. Using the GUI Tool:**
1. Run `python ConvertGUI.py`
2. Paste your BibTeX entries in the input area
3. Click "Batch Convert" button
4. Copy the results and paste into your LaTeX document
5. Add insights and tags manually as needed

**2. Using the Core Library:**
```python
# Example: Convert and add insights programmatically
converter = BibConverter()
bib_entry = """@article{Transformer2017,
title={Attention Is All You Need},
author={Vaswani, Ashish and others},
year={2017}
}"""

base_result = converter.convert_bib_to_addliterature(bib_entry)
# Add your insights and tags
final_result = base_result.replace('{}{}', '{Revolutionary self-attention mechanism that eliminates RNNs and CNNs}{NLP,Attention,Transformer}')
```

**3. Integration Workflow:**
```latex
% 1. Convert BibTeX using tools
% 2. Add insights and tags
\addliterature{Attention Is All You Need\cite{Vaswani2017}}{Vaswani et al.}{2017}{Introduces Transformer architecture based entirely on attention mechanisms, eliminating recurrence and convolution for parallelizable training}{NLP,Attention}

% 3. Use in your document
\sortbyyear
\showfullreviewinline  % 🆕 Recommended: Use inline format
```

## Core Functions

### Data Input

#### `\addliterature{title}{authors}{year}{insight}{tag}`
Add literature with full information including tags.

```latex
\addliterature{Attention Is All You Need}{Vaswani et al.}{2017}{Transformer architecture}{NLP,Attention}
```

#### `\addliteratureold{title}{authors}{year}{insight}`
Legacy command for backward compatibility (no tags).

```latex
\addliteratureold{BERT Paper}{Devlin et al.}{2018}{Bidirectional encoding}
```

### Sorting Functions

#### `\sortbyyear`
Sort by publication year (earliest to latest).

```latex
\sortbyyear
```

#### `\sortbytitle`
Sort alphabetically by title.

```latex
\sortbytitle
```

#### `\sortbyauthors`
Sort alphabetically by author names.

```latex
\sortbyauthors
```

#### `\sortbytag`
Sort alphabetically by tags.

```latex
\sortbytag
```

#### `\sortbyyeartitle`
Sort by year first, then by title.

```latex
\sortbyyeartitle
```

#### `\sortbytagyear`
Sort by tag first, then by year.

```latex
\sortbytagyear
```

#### `\sortby{field}`
Sort by any database field.

```latex
\sortby{authors}
```

### Display Functions

#### Standard Display Functions

#### `\showfullreview`
Display all literature in detailed table format.

```latex
\showfullreview
```

#### `\showbasiclist`
Display literature in compact list format.

```latex
\showbasiclist
```

#### `\showbasiclistwithinsight`
Display compact list including research insights.

```latex
\showbasiclistwithinsight
```

#### 🆕 Inline Format Functions

**Recommended for better table spacing and readability:**

#### `\showfullreviewinline`
Display detailed table with inline format insights (solves spacing issues).

```latex
\showfullreviewinline  % 🆕 Recommended
```

#### `\showbasiclistinline`
Display compact list with inline format insights.

```latex
\showbasiclistinline
```

#### 🆕 Compact Format Functions

**For maximum space efficiency:**

#### `\showfullreviewcompact`
Display detailed table with compact format (minimal spacing).

```latex
\showfullreviewcompact
```

#### `\showbasiclistcompact`
Display compact list with minimal spacing.

```latex
\showbasiclistcompact
```

### Tag-Based Filtering

#### Standard Tag Filtering

#### `\showfullreviewbytag{tag}`
Show detailed view of papers with specific tag.

```latex
\showfullreviewbytag{NLP}
```

#### `\showbasiclistbytag{tag}`
Show compact list of papers with specific tag.

```latex
\showbasiclistbytag{AI}
```

#### `\showbasiclistwithinsightbytag{tag}`
Show compact list with insights for specific tag.

```latex
\showbasiclistwithinsightbytag{DeepLearning}
```

#### 🆕 Inline Format Tag Filtering

**Recommended for better display:**

#### `\showfullreviewbytaginline{tag}`
Show detailed view with inline format for specific tag.

```latex
\showfullreviewbytaginline{NLP}  % 🆕 Recommended
```

#### `\showbasiclistbytaginline{tag}`
Show compact list with inline format for specific tag.

```latex
\showbasiclistbytaginline{AI}
```

#### 🆕 Compact Format Tag Filtering

#### `\showfullreviewbytagcompact{tag}`
Show detailed view with compact format for specific tag.

```latex
\showfullreviewbytagcompact{NLP}
```

#### `\showbasiclistbytagcompact{tag}`
Show compact list with compact format for specific tag.

```latex
\showbasiclistbytagcompact{AI}
```

### 🆕 Inline Format Helpers

Use these commands to create consistent inline formatting:

#### `\inlineitem{text}`
Create bold inline item.

```latex
\inlineitem{Key Contributions:}  % → **Key Contributions:**
```

#### `\inlinesep`
Insert bullet separator.

```latex
Contribution1 \inlinesep Contribution2  % → Contribution1 • Contribution2
```

#### `\inlinearrow`
Insert arrow separator.

```latex
Method \inlinearrow Result  % → Method → Result
```

### Statistics and Information

#### `\showstats`
Display database statistics and available tags.

```latex
\showstats
```

#### `\getpapercount`
Get total number of papers.

```latex
Total papers: \getpapercount
```

#### `\showavailabletags`
Display all available tags in the database.

```latex
\showavailabletags
```

#### `\systeminfo`
Show system version and feature information.

```latex
\systeminfo
```

### Database Management

#### `\clearliterature`
Clear all literature from database.

```latex
\clearliterature
```

#### `\resetpapercount`
Reset paper numbering counter.

```latex
\resetpapercount
```

## 🆕 Recommended Usage Patterns

### Best Practices for v3.0

**1. Use Inline Format for Better Display:**
```latex
% ✅ Recommended: Inline format
\addliterature{Paper Title}{Authors}{2023}{
\textbf{Key Contributions:} Contribution1 • Contribution2 • Contribution3 \textbf{Methods:} Method description \textbf{Conclusions:} Conclusion description
}{Tag1,Tag2}

% Display with inline format
\showfullreviewinline
```

**2. Organize with Tags and Sorting:**
```latex
% Sort by tag first, then by year
\sortbytagyear
\showfullreviewinline
```

**3. Use Compact Format for Space-Constrained Documents:**
```latex
\showfullreviewcompact  % Minimal spacing
```

**4. Filter by Tags with Inline Display:**
```latex
\showfullreviewbytaginline{NLP}  % Show only NLP papers with inline format
```

## Complete Example

```latex
\documentclass{article}
\input{literature-system.tex}

\begin{document}

% Add literature with inline format insights (converted from BibTeX using our tools)
\addliterature{Attention Is All You Need\cite{Vaswani2017}}{Vaswani et al.}{2017}{
\textbf{Core Innovation:} Proposes Transformer architecture • Entirely based on self-attention mechanism • Eliminates recurrence and convolution \textbf{Impact:} Foundation for large language models • Enables parallelizable training
}{NLP,Attention}

\addliterature{BERT\cite{Devlin2018}}{Devlin et al.}{2018}{
\textbf{Breakthrough:} Bidirectional encoding representations • Masked language model pre-training \textbf{Achievement:} SOTA on 11 NLP tasks • Deep bidirectional representation learning
}{NLP,BERT}

\addliterature{GPT-3\cite{Brown2020}}{Brown et al.}{2020}{
\textbf{Scale:} 175 billion parameters • Few-shot learning capabilities \textbf{Significance:} Multi-task zero/few-shot learning • Demonstrates potential for artificial general intelligence
}{NLP,GPT}

% Sort and display with recommended inline format
\sortbyyear
\showstats

% 🆕 Use inline format for better display
\showfullreviewinline

% Filter by tag with inline format
\showfullreviewbytaginline{NLP}

% Show usage guide
\showusageguide

\end{document}
```

## Key Features

- **Smart Empty Handling**: Empty insights display as ∅
- **Multi-tag Support**: Comma-separated tags (e.g., "AI,NLP,Transformer")
- **Cross-page Tables**: Uses `longtable` for long literature lists
- **Color-coded Tags**: Tags display in blue monospace font
- **Flexible Sorting**: Multiple sorting criteria and combinations
- **Comprehensive Insight Recording**: Detailed note-taking system for literature review
- **🆕 BibTeX Integration**: Automated conversion tools for seamless workflow
- **🆕 Batch Processing**: Handle multiple entries simultaneously
- **🆕 GUI Interface**: User-friendly desktop application
- **🆕 Citation Integration**: Automatic `\cite{}` command insertion
- **🆕 Inline Format Support**: Solves table spacing issues with itemize environments
- **🆕 Compact Display Options**: Multiple format variants for different space requirements
- **🆕 Format Helpers**: Consistent inline formatting tools
- **🆕 Usage Guide**: Built-in help system with `\showusageguide`

---

*Version 3.0 - Enhanced with inline format support, compact display options, and improved table spacing*