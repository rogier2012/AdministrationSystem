from gyara.models import Transaction, Category


def get_category_prediction(user,description):
    objects = Transaction.objects.all().filter(user_id=user).filter(category__isnull=False)
    result = dict()
    for obj in objects:
        map = result.get(obj.description.lower(),dict())
        map[obj.category_id] = map.get(obj.category_id, 0) + 1
        result[obj.description.lower()] = map

    lowercase_description = description.lower()
    for desc, categories in result.items():
        if desc in lowercase_description:
            cat_id = max(categories,key=categories.get)

            return cat_id

    return ""
