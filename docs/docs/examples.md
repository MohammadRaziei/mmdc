---
sidebar_position: 2
---

# Examples

## Basic Flowchart

Create a file `flowchart.mermaid`:

```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

Convert to different formats:

```bash
# To SVG
mmdc --input flowchart.mermaid --output flowchart.svg

# To PNG
mmdc --input flowchart.mermaid --output flowchart.png

# To PDF
mmdc --input flowchart.mermaid --output flowchart.pdf
```

## Sequence Diagram

Create a file `sequence.mermaid`:

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob, how are you?
    Bob-->>Alice: I'm good thanks!
```

Convert to different formats:

```bash
mmdc --input sequence.mermaid --output sequence.png
```

## Gantt Chart

Create a file `gantt.mermaid`:

```mermaid
gantt
    title A Gantt Diagram
    dateFormat  YYYY-MM-DD
    section Section
    A task           :a1, 2014-01-01, 30d
    Another task     :after a1, 20d
    section Another
    Task in sec      :2014-01-12, 12d
    another task     :24d
```

Convert with custom timeout for complex diagrams:

```bash
mmdc --input gantt.mermaid --output gantt.pdf --timeout 60
```

## Class Diagram

Create a file `class.mermaid`:

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    Animal <|-- Dog
```

Convert to PNG with custom styling:

```bash
mmdc --input class.mermaid --output class.png --width 800 --height 600
```

## Pie Chart

Create a file `pie.mermaid`:

```mermaid
pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rabbits" : 15
```

Convert to SVG:

```bash
mmdc --input pie.mermaid --output pie.svg
```