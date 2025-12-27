from bson import ObjectId

def serialize_object_id(doc):
    if isinstance(doc, list):
        return [serialize_object_id(d) for d in doc]

    if isinstance(doc, dict):
        return {
            k: serialize_object_id(v) if isinstance(v, (dict, list, ObjectId)) else v
            for k, v in doc.items()
        }

    if isinstance(doc, ObjectId):
        return str(doc)

    return doc