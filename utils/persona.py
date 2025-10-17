from dataclasses import dataclass, field
from typing import List, Optional, Union, Any, Dict
import random

RangeOrOptions = Optional[Union[List[str], List[int], List[float]]]  # None, ["a","b"], or [min,max]

def _is_numeric_range(v: Any) -> bool:
    return isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v)

def _sample_from(spec: RangeOrOptions, rng: random.Random) -> Optional[Union[str, int, float]]:
    if spec is None:
        return None
    if _is_numeric_range(spec):
        lo, hi = spec
        # If both ints, return int; otherwise return float with 1 decimal for readability
        if all(isinstance(x, int) for x in (lo, hi)):
            return rng.randint(int(lo), int(hi))
        else:
            return round(rng.uniform(float(lo), float(hi)), 1)
    if isinstance(spec, list) and len(spec) > 0:
        return rng.choice(spec)
    return None

@dataclass
class Demographic:
    age: RangeOrOptions = None                      # e.g., [18, 35]
    gender: RangeOrOptions = None                   # e.g., ["male", "female", "non-binary"]
    income_level: RangeOrOptions = None             # e.g., ["low", "medium", "high"]
    education_level: RangeOrOptions = None          # e.g., ["high school", "bachelor's", "master's"]
    marital_status: RangeOrOptions = None           # e.g., ["single", "married", "divorced"]
    household_size: RangeOrOptions = None           # e.g., [1, 5]
    children_count: RangeOrOptions = None           # e.g., [0, 3]
    occupation: RangeOrOptions = None               # e.g., ["student", "professional", "retired"]

@dataclass
class Geographic:
    country: RangeOrOptions = None                  # e.g., ["US", "UK", "Germany"]
    region: RangeOrOptions = None                   # e.g., ["Northeast", "South"]
    urbanicity: RangeOrOptions = None               # e.g., ["urban", "suburban", "rural"]
    climate: RangeOrOptions = None                  # e.g., ["temperate", "tropical"]

@dataclass
class Psychographic:
    lifestyle: RangeOrOptions = None                # e.g., ["health-conscious", "budget-conscious"]
    values: RangeOrOptions = None                   # e.g., ["sustainability", "convenience", "status"]
    personality: RangeOrOptions = None              # e.g., ["analytical", "impulsive", "open-minded"]
    interests: RangeOrOptions = None                # e.g., ["fitness", "gaming", "beauty", "cooking"]

@dataclass
class Behavioral:
    purchase_frequency: RangeOrOptions = None       # e.g., ["light", "medium", "heavy"]
    brand_loyalty: RangeOrOptions = None            # e.g., ["loyalist", "switcher", "new entrant"]
    purchase_channel: RangeOrOptions = None         # e.g., ["online", "in-store", "subscription"]
    category_experience: RangeOrOptions = None      # e.g., ["low", "moderate", "high"]

@dataclass
class Technographic:
    devices: RangeOrOptions = None                  # e.g., ["smartphone", "tablet", "smartwatch"]
    social_media: RangeOrOptions = None             # e.g., ["TikTok", "Instagram", "YouTube"]
    tech_adoption: RangeOrOptions = None            # e.g., ["early adopter", "mainstream", "tech-averse"]

@dataclass
class PersonaSpec:
    demographic: Demographic = field(default_factory=Demographic)
    geographic: Geographic = field(default_factory=Geographic)
    psychographic: Psychographic = field(default_factory=Psychographic)
    behavioral: Behavioral = field(default_factory=Behavioral)
    technographic: Technographic = field(default_factory=Technographic)

    # Sentence templates per field (only used if that field is not None)
    _templates: Dict[str, str] = field(default_factory=lambda: {
        # Demographic
        "demographic.age": "You are {age} years old.",
        "demographic.gender": "You identify as {gender}.",
        "demographic.income_level": "You have a {income_level} income level.",
        "demographic.education_level": "Your highest education level is {education_level}.",
        "demographic.marital_status": "You are {marital_status}.",
        "demographic.household_size": "Your household consists of {household_size} people.",
        "demographic.children_count": "You have {children_count} children.",
        "demographic.occupation": "You work as a {occupation}.",

        # Geographic
        "geographic.country": "You live in {country}.",
        "geographic.region": "Your region is {region}.",
        "geographic.urbanicity": "You live in a(n) {urbanicity} area.",
        "geographic.climate": "Your local climate is {climate}.",

        # Psychographic
        "psychographic.lifestyle": "Your lifestyle is {lifestyle}.",
        "psychographic.values": "You value {values}.",
        "psychographic.personality": "Your personality is {personality}.",
        "psychographic.interests": "Your interests include {interests}.",

        # Behavioral
        "behavioral.purchase_frequency": "You are a {purchase_frequency} buyer in this category.",
        "behavioral.brand_loyalty": "You are a {brand_loyalty} when it comes to brands.",
        "behavioral.purchase_channel": "You typically buy via {purchase_channel}.",
        "behavioral.category_experience": "Your experience with this category is {category_experience}.",

        # Technographic
        "technographic.devices": "You regularly use: {devices}.",
        "technographic.social_media": "Your preferred social platforms include: {social_media}.",
        "technographic.tech_adoption": "You are a {tech_adoption} of technology.",
    })

    def generate_biography(self, seed: Optional[int] = None) -> str:
        """
        Randomly samples values from provided specs (skipping None)
        and returns a single biography string.
        """
        rng = random.Random(seed)

        # Walk through nested specs and sample values
        parts = []

        def add_sentence(path: str, value_key: str, spec: RangeOrOptions, postprocess=None):
            sampled = _sample_from(spec, rng)
            if sampled is None:
                return
            if isinstance(sampled, list):  # if someone passed a list of lists by mistake
                if len(sampled) == 0:
                    return
                sampled_value = ", ".join(map(str, sampled))
            else:
                sampled_value = sampled

            if postprocess:
                sampled_value = postprocess(sampled_value)

            template = self._templates.get(path)
            if template:
                parts.append(template.format(**{value_key: sampled_value}))

        # Demographic
        add_sentence("demographic.age", "age", self.demographic.age)
        add_sentence("demographic.gender", "gender", self.demographic.gender)
        add_sentence("demographic.income_level", "income_level", self.demographic.income_level)
        add_sentence("demographic.education_level", "education_level", self.demographic.education_level)
        add_sentence("demographic.marital_status", "marital_status", self.demographic.marital_status)
        add_sentence("demographic.household_size", "household_size", self.demographic.household_size)
        add_sentence("demographic.children_count", "children_count", self.demographic.children_count)
        add_sentence("demographic.occupation", "occupation", self.demographic.occupation)

        # Geographic
        add_sentence("geographic.country", "country", self.geographic.country)
        add_sentence("geographic.region", "region", self.geographic.region)
        add_sentence("geographic.urbanicity", "urbanicity", self.geographic.urbanicity)
        add_sentence("geographic.climate", "climate", self.geographic.climate)

        # Psychographic
        add_sentence("psychographic.lifestyle", "lifestyle", self.psychographic.lifestyle)
        add_sentence("psychographic.values", "values", self.psychographic.values,
                     postprocess=lambda v: v if isinstance(v, str) else ", ".join(v) if isinstance(v, list) else v)
        add_sentence("psychographic.personality", "personality", self.psychographic.personality)
        add_sentence("psychographic.interests", "interests", self.psychographic.interests,
                     postprocess=lambda v: v if isinstance(v, str) else ", ".join(v) if isinstance(v, list) else v)

        # Behavioral
        add_sentence("behavioral.purchase_frequency", "purchase_frequency", self.behavioral.purchase_frequency)
        add_sentence("behavioral.brand_loyalty", "brand_loyalty", self.behavioral.brand_loyalty)
        add_sentence("behavioral.purchase_channel", "purchase_channel", self.behavioral.purchase_channel)
        add_sentence("behavioral.category_experience", "category_experience", self.behavioral.category_experience)

        # Technographic
        add_sentence("technographic.devices", "devices", self.technographic.devices,
                     postprocess=lambda v: v if isinstance(v, str) else ", ".join(v) if isinstance(v, list) else v)
        add_sentence("technographic.social_media", "social_media", self.technographic.social_media,
                     postprocess=lambda v: v if isinstance(v, str) else ", ".join(v) if isinstance(v, list) else v)
        add_sentence("technographic.tech_adoption", "tech_adoption", self.technographic.tech_adoption)

        # Join into a single, readable paragraph
        return " ".join(parts)


# -------------------------
# Example usage (proof of concept):
# -------------------------
if __name__ == "__main__":
    persona = PersonaSpec(
        demographic=Demographic(
            age=[18, 35],
            gender=["male", "female", "non-binary"],
            income_level=["low", "medium", "high"],
            education_level=["high school", "a bachelors degree", "a masters degree"],
            marital_status=["single", "married", "divorced"],
            household_size=[1, 5],
            children_count=[0, 3],
            occupation=["student", "professional", "freelancer", "retired"]
        ),
        geographic=Geographic(
            country=["US", "UK", "Germany", "Netherlands"],
            region=["Northeast", "West", "South", "Randstad"],
            urbanicity=["urban", "suburban", "rural"]
        ),
        psychographic=Psychographic(
            lifestyle=["health-conscious", "budget-conscious", "eco-conscious", "trend-oriented"],
            values=["sustainability", "convenience", "quality", "status"],
            personality=["analytical", "open-minded", "impulsive"],
            interests=["fitness", "gaming", "beauty", "cooking", "travel"]
        ),
        behavioral=Behavioral(
            purchase_frequency=["light", "medium", "heavy"],
            brand_loyalty=["loyalist", "switcher", "new entrant"],
            purchase_channel=["online", "in-store", "subscription"],
            category_experience=["low", "moderate", "high"]
        ),
        technographic=Technographic(
            devices=["smartphone", "tablet", "smartwatch", "laptop"],
            social_media=["TikTok", "Instagram", "YouTube", "LinkedIn"],
            tech_adoption=["early adopter", "mainstream", "tech-averse"]
        )
    )

    print(persona.generate_biography())
    print(persona.generate_biography())	