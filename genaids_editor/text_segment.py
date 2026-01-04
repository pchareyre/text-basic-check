"""
Modèle unifié pour représenter segments de texte éditables dans documents OOXML.

## Concepts Clés

### Qu'est-ce qu'un Segment ?

Un **Segment** est l'unité textuelle éditable dans un document OOXML (Word, PowerPoint, Excel).
Il représente un bloc de contenu cohérent qui peut être :
- Un paragraphe (texte normal)
- Un titre (Heading 1, 2, 3, etc.)
- Une cellule de tableau
- Un élément de liste (futur support)

### Anatomie d'un Segment

```
Segment (paragraphe)
├── text_id: "p0"                    # Identifiant unique
├── text: "Bonjour le monde"         # Texte complet (concaténation runs)
├── type: "paragraph"                # Type segment
└── runs: [                          # Runs individuels (granularité fine)
    ├── Run(id="p0_r0", text="Bonjour", bold=True, protected=False)
    └── Run(id="p0_r1", text=" le monde", bold=False, protected=False)
]
```

### Pourquoi Segment (et pas juste Paragraph) ?

1. **Abstraction unifiée** : Même interface pour paragraphes, titres, cellules
2. **Granularité run** : Préserve formatage détaillé (gras, italique, couleur)
3. **Protection fine** : Hyperliens, champs, content controls préservés run par run
4. **Réintégration sans perte** : Mapping lxml pour modifications XML directes

## Architecture V2

### Hiérarchie

```
Document DOCX
├── Segment (p0) → Paragraphe normal
│   ├── Run (p0_r0) → "Texte en gras" [bold=True]
│   └── Run (p0_r1) → " suite normale" [bold=False]
│
├── Segment (p1) → Titre (Heading 1)
│   └── Run (p1_r0) → "Introduction" [level=1]
│
├── Segment (t0_0_0) → Cellule tableau
│   ├── Run (t0_0_0_p0_r0) → "Ligne 1, Colonne 1"
│   └── Run (t0_0_0_p1_r0) → "Deuxième paragraphe cellule"
│
└── Segment (p2) → Paragraphe avec hyperlien
    ├── Run (p2_r0) → "Visitez " [protected=False]
    ├── Run (p2_r1) → "notre site" [protected=True, hyperlink]
    └── Run (p2_r2) → " pour plus d'infos" [protected=False]
```

### Run vs Segment

| Aspect | Run | Segment |
|--------|-----|---------|
| **Granularité** | Unité atomique texte | Bloc cohérent (paragraphe, cellule) |
| **Formatage** | Homogène (1 style) | Hétérogène (multiple styles) |
| **Édition** | Modifié individuellement | Modifié globalement (avec préservation runs) |
| **Protection** | Oui (hyperlien, field) | Oui (agrégation runs protégés) |
| **text_id** | `p0_r0` (run) | `p0` (segment) |

## Cas d'Usage

### 1. Édition Simple (sans protection)

```python
# Charger document
result = extract_docx_structure("doc.docx")

# Éditer segment
segment = result.segments[0]  # Premier paragraphe
segment.replace_text("Nouveau texte", ignore_protected_runs=False)

# Sauvegarder
apply_corrections_to_document(...)
```

### 2. Édition avec Préservation Hyperliens

```python
# Segment avec hyperlien
# Original: "Visitez notre site pour plus d'infos"
#           "Visitez " + [LIEN:notre site] + " pour plus d'infos"

segment = result.segments[5]
print(segment.text)  # "Visitez notre site pour plus d'infos"
print(segment.protected_runs)  # ["p5_r1"]

# Éditer en préservant hyperlien
segment.replace_text("Consultez notre site pour détails", ignore_protected_runs=True)

# Résultat: "Consultez " + [LIEN:notre site] + " pour détails"
# ✅ Hyperlien préservé automatiquement
```

### 3. Filtrage Segments

```python
# Tous paragraphes normaux
paragraphs = [s for s in result.segments if s.type == "paragraph"]

# Tous titres
headings = [s for s in result.segments if s.type == "heading"]

# Titres niveau 1 uniquement
h1_segments = [s for s in headings if s.metadata.get("level") == 1]

# Cellules tableau
table_cells = [s for s in result.segments if s.type == "table_cell"]
```

### 4. Analyse Protection

```python
segment = result.segments[0]

# Runs modifiables
unprotected = segment.get_unprotected_runs()
print(f"Modifiables: {len(unprotected)}")

# Texte protégé (hyperliens, champs)
protected_text = segment.get_protected_text()
print(f"Protege: {protected_text}")

# Ratio protection
ratio = len(segment.protected_runs) / len(segment.runs)
print(f"Protection: {ratio*100:.1f}%")
```

## Limitations Connues

### 1. Structure Complexe
**Segment actuel** : Capture uniquement texte plat (runs)
**Non supporté** : Tableaux imbriqués, graphiques, SmartArt dans paragraphe

```python
# ❌ Pas encore supporté
segment_with_chart = Segment(
    text_id="p10",
    text="[GRAPHIQUE]",  # Placeholder
    type="paragraph",
    runs=[],  # Vide (contenu non textuel)
    metadata={"contains_chart": True}
)
```

### 2. Protection Transverse
**Limitation** : Content controls multi-paragraphes détectés mais difficiles à éditer

```python
# Content control s'étendant sur 3 paragraphes
# ❌ Édition partielle casse la structure
segment1.replace_text("Nouveau texte para 1")  # Brise content control
```

**Solution future** : Ajouter `parent_content_control_id` dans metadata

### 3. Ordre Document
**Limitation** : `segments[]` suit ordre extraction (document → tables → headers)
**Non garanti** : Ordre visuel exact (tables flottantes, colonnes)

```python
# Ordre actuel
segments = [p0, p1, p2, t0_0_0, t0_0_1, ..., header1_p0]

# Ordre visuel réel (peut différer si table flottante)
# p0, [TABLE], p1, p2
```

## V2 Features

✅ **Granularité run** : Préservation formatage détaillé
✅ **Protection multi-niveaux** : Hyperliens, fields, content controls
✅ **Mapping lxml** : Réintégration sans perte
✅ **Typing fort** : Dataclass avec autocomplétion IDE
✅ **Compatible** : docx_json_extractor + reintegration.py

## Migration depuis V1

### Avant (V1)
```python
# JSON dict non typé
json_dict, run_map, doc = map_docx_to_json("doc.docx")

# Reconstruction manuelle
for element in json_dict["content"]:
    text_id = element["text_id"]
    text = element["text"]
    # ... pas de typing, pas de méthodes helper
```

### Après (V2)
```python
# Segment[] typé directement
result = extract_docx_structure("doc.docx")

# API haut niveau
for segment in result.segments:
    print(segment.text_id)  # Autocomplétion IDE
    unprotected = segment.get_unprotected_runs()  # Méthodes helper
    segment.replace_text("Nouveau", ignore_protected_runs=True)
```

## Références


- **DocxTextEditor** : API haut niveau (load/edit/save)
- **DocxContentControlEditor** : Insertions SDT/bookmarks (complémentaire)

## Glossaire

- **Run** : Unité atomique texte avec formatage homogène (w:r en XML)
- **Segment** : Bloc cohérent (paragraphe, titre, cellule)
- **text_id** : Identifiant unique segment (`p0`, `t0_0_0`, `h1_p5`)
- **run_id** : Identifiant unique run (`p0_r0`, `t0_0_0_p1_r2`)
- **protected_run** : Run non modifiable (hyperlien, field, content control)
- **run_element_map** : {run_id → lxml._Element} pour réintégration
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class Run:
    """
    Représente un run de texte avec formatage homogène.

    Un **run** (w:r en XML OOXML) est l'unité atomique de texte dans Word/PowerPoint/Excel.
    Chaque run a un formatage cohérent : si vous changez de gras à normal, c'est un nouveau run.

    ## Anatomie Run

    ```xml
    <w:r>                              <!-- Run element -->
      <w:rPr>                          <!-- Run properties -->
        <w:b/>                         <!-- Bold -->
        <w:i/>                         <!-- Italic -->
        <w:sz w:val="24"/>            <!-- Font size 12pt -->
        <w:color w:val="FF0000"/>     <!-- Red color -->
      </w:rPr>
      <w:t>Hello World</w:t>          <!-- Text content -->
    </w:r>
    ```
        - Si ignore_protected_runs=True: garde runs protégés, remplace les autres
        - Sinon: remplace tout (écrase protection)
    ## Exemples Réels

            ignore_protected_runs: Si True, laisse intacts les runs protégés
    # Run simple (texte normal)
        if ignore_protected_runs:
        run_id="p0_r0",
        text="Bonjour",
        run_props={"bold": False, "italic": False},
        is_protected=False
    )

    # Run formaté (gras + italique)
    run2 = Run(
        run_id="p0_r1",
        text=" le monde",
        run_props={"bold": True, "italic": True, "font_size": 14},
        is_protected=False
    )

    # Run protégé (hyperlien)
    run3 = Run(
        run_id="p5_r1",
        text="notre site",
        run_props={"underline": True, "color": "0000FF"},
        is_protected=True  # ← Hyperlien, ne doit pas être modifié
    )
    ```

    ## Propriétés Formatage Supportées

    | Propriété | Type | Description | Exemple XML |
    |-----------|------|-------------|-------------|
    | `bold` | bool | Texte en gras | `<w:b/>` |
    | `italic` | bool | Texte italique | `<w:i/>` |
    | `underline` | bool | Texte souligné | `<w:u w:val="single"/>` |
    | `strike` | bool | Texte barré | `<w:strike/>` |
    | `font_size` | int | Taille police (pt) | `<w:sz w:val="24"/>` (12pt) |
    | `color` | str | Couleur texte (hex) | `<w:color w:val="FF0000"/>` |
    | `highlight` | str | Surbrillance | `<w:highlight w:val="yellow"/>` |
    | `font_name` | str | Police | `<w:rFonts w:ascii="Arial"/>` |

    ## Protection Run

    Un run est **protégé** (is_protected=True) s'il contient :
    - **Hyperlien** : `<w:hyperlink>` wrapping le run
    - **Field** : `<w:fldChar>` (numéro page, date, etc.)
    - **Content Control** : `<w:sdt>` avec tag spécifique

    **Comportement édition :**
    ```python
    # Segment avec runs protégés
    segment = Segment(
        text="Visitez notre site pour infos",
        runs=[
            Run("p0_r0", "Visitez ", protected=False),
            Run("p0_r1", "notre site", protected=True),  # Hyperlien
            Run("p0_r2", " pour infos", protected=False)
        ]
    )

    # Édition avec préservation
    segment.replace_text("Consultez notre site pour détails", ignore_protected_runs=True)

    # Résultat : "Consultez " + [LIEN:notre site] + " pour détails"
    # ✅ Run protégé (hyperlien) préservé automatiquement
    ```

    Attributes:
        run_id: Identifiant unique (ex: "p0_r0", "t0_0_0_p0_r1")
        text: Contenu textuel du run
        run_props: Propriétés formatage (bold, italic, font_size, color, etc.)
        is_protected: True si run protégé (hyperlien, content control, field)
        _lxml_element: Référence élément lxml (pour réintégration)

    Examples:
        >>> # Run basique
        >>> run = Run(
        ...     run_id="p0_r0",
        ...     text="Hello",
        ...     run_props={"bold": True, "font_size": 12},
        ...     is_protected=False
        ... )
        >>> print(run.text)
        Hello
    """

    run_id: str
    text: str
    run_props: Dict[str, Any] = field(default_factory=dict)
    is_protected: bool = False

    # Référence lxml (pour réintégration, non sérialisable)
    _lxml_element: Optional[Any] = field(default=None, repr=False, compare=False)


@dataclass
class Segment:
    """
    Unité textuelle éditable (paragraphe, cellule tableau, etc.).

    V2 Features:
    - Granularité run (pas juste paragraphe.text)
    - Protection run-level (préserve hyperliens, content controls)
    - Mapping lxml (réintégration sans perte formatage)
    - Compatible docx_json_extractor + reintegration.py

    Attributes:
        text_id: Identifiant unique segment (`p0`, `t0_0_0`, `h1_p5`)
        text: Texte complet (concaténation runs, lecture seule)
        type: Type segment ("paragraph", "heading", "table_cell")
        runs: Liste runs individuels (granularité fine)
        protected_runs: Liste run_id protégés (hyperliens, fields)
        text_fields: Champs texte (DOCX fields, formulas)
        styles: Styles agrégés (ou premier run)
        metadata: Métadonnées (level, outline_level, table_index, etc.)
        _lxml_paragraph: Référence paragraphe lxml (réintégration XML)

    Examples:
        >>> # Créer segment manuel
        >>> segment = Segment(
        ...     text_id="p0",
        ...     text="Hello world",
        ...     type="paragraph",
        ...     runs=[
        ...         Run("p0_r0", "Hello", {"bold": True}),
        ...         Run("p0_r1", " world", {})
        ...     ]
        ... )
        >>> print(segment.text)
        Hello world
        >>> print(len(segment.get_unprotected_runs()))
        2

        >>> # Éditer segment
        >>> segment.replace_text("Bonjour monde", ignore_protected_runs=False)
        >>> print(segment.text)
        Bonjour monde

    See Also:
        - Run : Unité atomique texte avec formatage
        - extract_docx_structure() : Extraction segments depuis DOCX
        - apply_corrections_to_document() : Réintégration segments modifiés
    """

    text_id: str
    text: str
    type: str

    # Runs individuels (granularité fine)
    runs: List[Run] = field(default_factory=list)

    # Protection
    protected_runs: List[str] = field(default_factory=list)
    text_fields: List[Dict[str, Any]] = field(default_factory=list)

    # Styles (agrégés ou premier run)
    styles: Dict[str, Any] = field(default_factory=dict)

    # Métadonnées
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Référence paragraphe lxml (pour réintégration, non sérialisable)
    _lxml_paragraph: Optional[Any] = field(default=None, repr=False, compare=False)

    @property
    def is_protected(self) -> bool:
        """
        Check if the entire segment is protected.

        Returns True if all runs in the segment are protected,
        or if the segment has no runs.

        Returns:
            True if all runs are protected, False otherwise
        """
        if not self.runs:
            return False
        return all(run.is_protected for run in self.runs)

    def get_unprotected_runs(self) -> List[Run]:
        """
        Retourne runs non protégés (modifiables).

        Filtre les runs avec `is_protected=False`, c'est-à-dire ceux qui ne contiennent
        pas d'hyperliens, fields, ou content controls.

        Returns:
            Liste runs modifiables (is_protected=False)

        Examples:
            >>> segment = Segment(
            ...     text_id="p0",
            ...     runs=[
            ...         Run("p0_r0", "Texte ", protected=False),
            ...         Run("p0_r1", "lien", protected=True),
            ...         Run("p0_r2", " suite", protected=False)
            ...     ]
            ... )
            >>> unprotected = segment.get_unprotected_runs()
            >>> print(len(unprotected))
            2
            >>> print([r.text for r in unprotected])
            ['Texte ', ' suite']
        """
        return [r for r in self.runs if not r.is_protected]

    def get_protected_text(self) -> str:
        """
        Retourne texte des runs protégés (hyperliens, etc.).

        Returns:
            Concaténation texte runs protégés

        Examples:
            >>> segment.get_protected_text()
            'https://example.com'
        """
        return "".join(r.text for r in self.runs if r.is_protected)

    def replace_text(self, new_text: str, ignore_protected_runs: bool = True) -> "Segment":
        """
        Remplace le texte en préservant ou non les runs protégés.

        Stratégie:
        - Si ignore_protected_runs=True: garde runs protégés, remplace les autres
        - Sinon: remplace tout (écrase protection)

        Args:
            new_text: Nouveau texte à insérer
            ignore_protected_runs: Si True, laisse intacts les runs protégés

        Returns:
            self (mutation in-place)

        Examples:
            >>> segment.replace_text("New text", ignore_protected_runs=True)
            >>> print(segment.text)
            New text
        """
        if ignore_protected_runs:
            # Distribution texte sur runs non protégés
            unprotected = self.get_unprotected_runs()
            if unprotected:
                unprotected[0].text = new_text
                for r in unprotected[1:]:
                    r.text = ""
        else:
            # Écrasement complet
            self.runs = [
                Run(run_id=f"{self.text_id}_r0", text=new_text, run_props={}, is_protected=False)
            ]
            self.protected_runs = []

        # Mettre à jour texte agrégé
        self.text = "".join(r.text for r in self.runs)
        return self

    @classmethod
    def from_json_dict(
        cls,
        json_element: Dict[str, Any],
        run_element_map: Optional[Dict[str, Any]] = None,
        protected_run_ids: Optional[Set[str]] = None,
    ) -> "Segment":
        """
        Crée Segment depuis dictionnaire JSON.

        Args:
            json_element: Dict élément JSON
            run_element_map: Mapping run_id → lxml._Element (optionnel)
            protected_run_ids: Set runs protégés (optionnel)

        Returns:
            Instance Segment

        Raises:
            ValueError: Si format JSON invalide

        Examples:
            >>> seg = Segment.from_json_dict({"text_id": "p0", ...}, run_map)
        """
        # Validation
        if not isinstance(json_element, dict):
            raise ValueError(f"json_element must be dict, got {type(json_element)}")

        if "text_id" not in json_element:
            raise ValueError("json_element missing required field: text_id")

        # Extraire runs
        runs_data = json_element.get("runs", [])
        runs: List[Run] = []

        for run_data in runs_data:
            run_id = run_data.get("run_id", "")
            run_text = run_data.get("text", "")
            run_props = run_data.get("run_props", {})

            # Déterminer protection
            is_protected = False
            if protected_run_ids:
                is_protected = run_id in protected_run_ids
            else:
                is_protected = run_data.get("is_protected", False)

            # Récupérer élément lxml si disponible
            lxml_element = None
            if run_element_map and run_id in run_element_map:
                lxml_element = run_element_map[run_id]

            run = Run(
                run_id=run_id,
                text=run_text,
                run_props=run_props,
                is_protected=is_protected,
                _lxml_element=lxml_element,
            )
            runs.append(run)

        # ✅ FIX: Gérer cas liste vide
        # Avant: styles=json_element.get("runs", [{}])[0].get("run_props", {})
        # Après: Extraire styles du premier run si existe, sinon dict vide
        styles = {}
        if runs:
            styles = runs[0].run_props.copy()  # Utiliser run parsé
        elif runs_data:  # Fallback: extraire de JSON si run list pas vide
            styles = runs_data[0].get("run_props", {})

        # Protected runs
        protected_runs_list = json_element.get("protected_runs", [])
        if protected_run_ids:
            # Recalculer depuis set fourni
            protected_runs_list = [r.run_id for r in runs if r.run_id in protected_run_ids]

        # Text fields
        text_fields = json_element.get("text_fields", [])

        # Metadata
        metadata = json_element.get("metadata", {})

        return cls(
            text_id=json_element["text_id"],
            text=json_element.get("text", ""),
            type=json_element.get("type", "paragraph"),
            runs=runs,
            protected_runs=protected_runs_list,
            text_fields=text_fields,
            styles=styles,
            metadata=metadata,
            _lxml_paragraph=None,  # Pas de lxml depuis JSON
        )
