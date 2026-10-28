from app.tools.market_tool import market_price_tool
from app.tools.weather_tool import weather_tool
from app.tools.crop_tool import crop_suitability_tool
from app.tools.profit_tool import profit_calculator_tool
from app.tools.rag_tool import rag_search_tool


print("\n===== MARKET TOOL =====")
print(market_price_tool("chilli"))

print("\n===== WEATHER TOOL =====")
print(weather_tool("markapur"))

print("\n===== CROP TOOL =====")
print(
    crop_suitability_tool(
        crop="chilli",
        soil="red",
        water="medium",
        season="kharif",
        temperature=29,
        rainfall=850
    )
)

print("\n===== PROFIT TOOL =====")
print(
    profit_calculator_tool(
        crop="chilli",
        yield_per_acre=2500,
        expected_price=120,
        cost_per_acre=35000,
        land_area=2
    )
)

print("\n===== RAG TOOL =====")
results = rag_search_tool("What type of soil is suitable for chilli?")
for result in results:
    print(result)
