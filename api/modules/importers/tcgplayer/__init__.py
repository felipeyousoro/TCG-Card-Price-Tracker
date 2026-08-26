"""TCGPlayer importer: curated groups plus pluggable fetch backends."""

from .groups import TcgplayerGroup, load_optcg_groups

__all__ = ["TcgplayerGroup", "load_optcg_groups"]
