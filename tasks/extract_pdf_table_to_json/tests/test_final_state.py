import json
import os
import pytest

PROJECT_DIR = "/home/user/sales_extraction"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "extract_sales.py")
OUTPUT_JSON = os.path.join(PROJECT_DIR, "sales.json")

EXPECTED_PRODUCTS = {
    "Widget": {"units_sold": 1200, "revenue_usd": 24000},
    "Gadget": {"units_sold": 850, "revenue_usd": 21250},
    "Sprocket": {"units_sold": 430, "revenue_usd": 12900},
    "Cog": {"units_sold": 670, "revenue_usd": 18760},
}


def _load_sales_json():
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def test_extract_script_exists():
    assert os.path.isfile(SCRIPT_PATH), (
        f"Expected the user's extraction script at {SCRIPT_PATH}, but it was not found."
    )


def test_extract_script_uses_llama_cloud_sdk():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "LlamaCloud" in content, (
        f"{SCRIPT_PATH} must reference the LlamaCloud client class from the llama_cloud SDK."
    )
    assert "llama_cloud" in content, (
        f"{SCRIPT_PATH} must import from the llama_cloud SDK."
    )
    assert "parsing.parse" in content, (
        f"{SCRIPT_PATH} must invoke client.parsing.parse(...) to start a LlamaParse job."
    )


def test_extract_script_does_not_hardcode_api_key():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "llx-" not in content, (
        f"{SCRIPT_PATH} appears to hardcode a LlamaCloud API key (found 'llx-' prefix). "
        "The script must rely on the LLAMA_CLOUD_API_KEY environment variable."
    )


def test_sales_json_exists_and_nonempty():
    assert os.path.isfile(OUTPUT_JSON), (
        f"Expected the extracted sales JSON at {OUTPUT_JSON}, but it was not found."
    )
    assert os.path.getsize(OUTPUT_JSON) > 0, (
        f"Output file {OUTPUT_JSON} exists but is empty."
    )


def test_sales_json_is_valid_json_object_with_products_key():
    data = _load_sales_json()
    assert isinstance(data, dict), (
        f"Top-level JSON value in {OUTPUT_JSON} must be an object, got {type(data).__name__}."
    )
    assert "products" in data, (
        f"Top-level JSON object in {OUTPUT_JSON} must contain a 'products' key. Got keys: {list(data.keys())}"
    )
    assert isinstance(data["products"], list), (
        f"'products' in {OUTPUT_JSON} must be a list, got {type(data['products']).__name__}."
    )


def test_sales_json_has_exactly_four_products():
    data = _load_sales_json()
    products = data["products"]
    assert len(products) == 4, (
        f"Expected exactly 4 product entries in {OUTPUT_JSON}, got {len(products)}: {products}"
    )


def test_sales_json_entry_schema():
    data = _load_sales_json()
    for i, product in enumerate(data["products"]):
        assert isinstance(product, dict), (
            f"Entry {i} in 'products' must be an object, got {type(product).__name__}: {product}"
        )
        for key in ("name", "units_sold", "revenue_usd"):
            assert key in product, (
                f"Entry {i} in 'products' is missing required key '{key}'. Got: {product}"
            )
        assert isinstance(product["name"], str), (
            f"Entry {i} 'name' must be a string, got {type(product['name']).__name__}: {product}"
        )
        assert isinstance(product["units_sold"], int) and not isinstance(
            product["units_sold"], bool
        ), (
            f"Entry {i} 'units_sold' must be an integer, got {type(product['units_sold']).__name__}: {product}"
        )
        assert isinstance(product["revenue_usd"], int) and not isinstance(
            product["revenue_usd"], bool
        ), (
            f"Entry {i} 'revenue_usd' must be an integer, got {type(product['revenue_usd']).__name__}: {product}"
        )


def test_sales_json_contains_all_expected_products_with_correct_values():
    data = _load_sales_json()
    by_name = {p["name"]: p for p in data["products"]}
    for name, expected in EXPECTED_PRODUCTS.items():
        assert name in by_name, (
            f"Expected product '{name}' to appear in {OUTPUT_JSON}. Got products: {list(by_name.keys())}"
        )
        actual = by_name[name]
        assert actual["units_sold"] == expected["units_sold"], (
            f"Product '{name}' has units_sold={actual['units_sold']} but expected {expected['units_sold']}."
        )
        assert actual["revenue_usd"] == expected["revenue_usd"], (
            f"Product '{name}' has revenue_usd={actual['revenue_usd']} but expected {expected['revenue_usd']}."
        )
