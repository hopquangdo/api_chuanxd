import uuid
import json

BASE_ITEM = {
    "id": "",
    "text": "",
    "doc_code": "TCVN 4451:2012",
    "doc_name": "NHÀ Ở - NGUYÊN TẮC CƠ BẢN ĐỂ THIẾT KẾ",
    "section": "",
    "page": None
}

def generate_items(n=100):
    items = []
    for _ in range(n):
        item = BASE_ITEM.copy()
        item["id"] = str(uuid.uuid4())
        items.append(item)
    return items

if __name__ == "__main__":
    data = generate_items(100)

    with open("dummy_chunks.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ DONE: generated {len(data)} empty chunks")
