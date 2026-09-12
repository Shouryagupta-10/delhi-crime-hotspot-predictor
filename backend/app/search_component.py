import os
import streamlit.components.v1 as components

_COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictive_search")
_tab2_predictive_search = components.declare_component("tab2_predictive_search", path=_COMPONENT_DIR)

def render_predictive_search(default_query: str = "", key: str = "tab2_search_bar"):
    return _tab2_predictive_search(default_query=default_query, key=key)

if __name__ == "__main__":
    print("Component declared successfully:", _tab2_predictive_search)
