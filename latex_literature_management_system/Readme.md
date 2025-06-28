# Latex Literature Management System

<!-- TOC -->

- [Latex Literature Management System](#latex-literature-management-system)
    - [What It Does](#what-it-does)
    - [Understanding the Insight Field](#understanding-the-insight-field)
    - [Installation](#installation)
    - [Download](#download)
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
            - [\showfullreview](#%5Cshowfullreview)
            - [\showbasiclist](#%5Cshowbasiclist)
            - [\showbasiclistwithinsight](#%5Cshowbasiclistwithinsight)
        - [Tag-Based Filtering](#tag-based-filtering)
            - [\showfullreviewbytag{tag}](#%5Cshowfullreviewbytagtag)
            - [\showbasiclistbytag{tag}](#%5Cshowbasiclistbytagtag)
            - [\showbasiclistwithinsightbytag{tag}](#%5Cshowbasiclistwithinsightbytagtag)
        - [Statistics and Information](#statistics-and-information)
            - [\showstats](#%5Cshowstats)
            - [\getpapercount](#%5Cgetpapercount)
            - [\showavailabletags](#%5Cshowavailabletags)
            - [\systeminfo](#%5Csysteminfo)
        - [Database Management](#database-management)
            - [\clearliterature](#%5Cclearliterature)
            - [\resetpapercount](#%5Cresetpapercount)
    - [Complete Example](#complete-example)
    - [Key Features](#key-features)

<!-- /TOC -->
<!-- /TOC -->

A LaTeX system for managing academic literature with automated sorting, tag-based filtering, and multiple display formats. Built on the `datatool` package for structured data storage and processing.

## What It Does

This system allows you to:
- Store literature data in a structured database
- Sort by multiple criteria (year, title, author, tags)
- Filter by tags for topic-based organization
- Display in various formats (detailed tables, compact lists)
- Generate statistics and analytics

## Understanding the Insight Field

**The Insight field serves as your literature reading notes**, designed to capture the essential value and your personal understanding of each paper. It is recommended to record:

- **Innovative Ideas**: Novel theories, concepts, or perspectives proposed in the literature
- **Key Methods**: Important research methods, technical approaches, or experimental designs employed
- **Main Conclusions**: Core findings and significant discoveries presented
- **Future Directions**: Suggestions or inspirations for future research directions
- **Personal Reflections**: Your own insights, questions, or application ideas after reading

**Examples:**
```latex
% Recording innovative methods
\addliterature{Attention Is All You Need}{Vaswani et al.}{2017}{Introduces Transformer architecture based entirely on attention mechanisms, eliminating recurrence and convolution for parallelizable training}{NLP,Attention}

% Recording key conclusions
\addliterature{BERT}{Devlin et al.}{2018}{Breakthrough in bidirectional encoding through masked language model pre-training, achieving state-of-the-art results across multiple NLP tasks}{NLP,BERT}

% Recording methodological innovation and implications
\addliterature{GPT-3}{Brown et al.}{2020}{Demonstrates few-shot learning capabilities of large-scale language models, 175B parameter model excels across diverse tasks, pointing toward artificial general intelligence}{NLP,GPT}
```

Through detailed insight recording, you can quickly review key paper points, facilitating future research and writing references.

## Installation

```latex
\input{literature-system.tex}
```

## Download

📥 **Get the LaTeX system file:**

- **Direct Download**: [literature-system.tex](./literature-system.tex)
- **Raw File**: [literature-system.tex (raw)](./literature-system.tex?raw=true)

Simply download the `literature-system.tex` file and place it in your LaTeX project directory, then include it using `\input{literature-system.tex}` in your document.

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

### Tag-Based Filtering

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

## Complete Example

```latex
\documentclass{article}
\input{literature-system.tex}

\begin{document}

% Add literature with detailed insights
\addliterature{Attention Is All You Need}{Vaswani et al.}{2017}{Introduces Transformer architecture based entirely on attention mechanisms, eliminating recurrence and convolution, enabling parallelizable training and laying foundation for large language models}{NLP,Attention}
\addliterature{BERT}{Devlin et al.}{2018}{Breakthrough in bidirectional encoding through masked language model pre-training, achieving deep bidirectional representations and setting new records on 11 NLP tasks}{NLP,BERT}
\addliterature{GPT-3}{Brown et al.}{2020}{Demonstrates few-shot learning capabilities of large-scale language models, 175B parameter model performs diverse tasks without fine-tuning, showcasing potential for artificial general intelligence}{NLP,GPT}

% Sort and display
\sortbyyear
\showstats
\showfullreview

% Filter by tag
\showbasiclistbytag{NLP}

\end{document}
```

## Key Features

- **Smart Empty Handling**: Empty insights display as ∅
- **Multi-tag Support**: Comma-separated tags (e.g., "AI,NLP,Transformer")
- **Cross-page Tables**: Uses `longtable` for long literature lists
- **Color-coded Tags**: Tags display in blue monospace font
- **Flexible Sorting**: Multiple sorting criteria and combinations
- **Comprehensive Insight Recording**: Detailed note-taking system for literature review

---

*Version 2.0 - Enhanced with tag support and insight documentation*
