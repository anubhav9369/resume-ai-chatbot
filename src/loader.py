# src/loader.py
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ResumeSection:
    name: str              # e.g. "experience", "education"
    content: str           # Raw text of that section
    tokens: int = 0        # Populated after tokenization


class ResumeLoader:
    """Parse a plain-text resume into structured sections."""

    # Keywords that signal the start of a new section
    SECTION_HEADERS = {
        "experience": ["experience", "work history", "employment", "professional experience"],
        "education": ["education", "academic background", "qualifications"],
        "skills": ["skills", "technical skills", "core competencies", "technologies"],
        "projects": ["projects", "key projects", "notable projects"],
        "certifications": ["certifications", "certificates", "licenses"],
        "summary": ["summary", "profile", "objective", "about"],
        "contact": ["contact", "personal details"],
    }

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.raw_text = self._read()
        self.sections = self._parse_sections()

    def _read(self) -> str:
        """Read and normalize whitespace."""
        text = self.filepath.read_text(encoding='utf-8')
        # Normalize multiple blank lines to single
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _parse_sections(self) -> dict[str, ResumeSection]:
        """Split resume into named sections by detecting section headers."""
        lines = self.raw_text.split('\n')
        sections = {}
        current_name = 'header'  # Content before first section header
        current_lines = []

        for line in lines:
            detected = self._detect_section(line)
            if detected:
                # Save the current section
                if current_lines:
                    sections[current_name] = ResumeSection(
                        name=current_name,
                        content='\n'.join(current_lines).strip()
                    )
                current_name = detected
                current_lines = []
            else:
                current_lines.append(line)

        # Don't forget the last section
        if current_lines:
            sections[current_name] = ResumeSection(
                name=current_name,
                content='\n'.join(current_lines).strip()
            )
        return sections

    def _detect_section(self, line: str) -> Optional[str]:
        """Return section name if this line is a section header, else None."""
        clean = line.lower().strip().rstrip(':')
        for section_name, keywords in self.SECTION_HEADERS.items():
            if clean in keywords:
                return section_name
        return None

    def get_section(self, name: str) -> str:
        """Get content of a specific section, or empty string if not found."""
        section = self.sections.get(name)
        return section.content if section else ''

    def get_full_text(self) -> str:
        """Return full resume text — used when all context fits in window."""
        return self.raw_text

    def get_context_for_question(self, question: str) -> str:
        """
        Smart section selector: return the most relevant section(s)
        based on keywords in the question.
        """
        q = question.lower()
        relevant = []

        if any(w in q for w in ['work', 'job', 'company', 'role', 'position', 'employer']):
            relevant.append('experience')
        if any(w in q for w in ['degree', 'university', 'college', 'study', 'major', 'gpa']):
            relevant.append('education')
        if any(w in q for w in ['skill', 'know', 'proficient', 'technology', 'language', 'tool']):
            relevant.append('skills')
        if any(w in q for w in ['project', 'built', 'developed', 'created']):
            relevant.append('projects')
        if any(w in q for w in ['cert', 'certificate', 'license']):
            relevant.append('certifications')

        # Always include header (name, contact) and summary
        relevant = ['header', 'summary'] + relevant

        # Collect text from relevant sections
        parts = [
            self.sections[s].content
            for s in relevant
            if s in self.sections and self.sections[s].content
        ]
        return '\n\n'.join(parts) if parts else self.raw_text
