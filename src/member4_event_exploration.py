
def normalize_name(name):
    return str(name).strip().lower().replace(" ", "_")


def find_column(columns, target):
    aliases = {
        "case": ["case_id", "caseid", "case"],
        "activity": ["activity_name", "activity", "event"],
        "timestamp": ["timestamp", "time", "datetime"],
    }

    possible_names = aliases.get(target, [target])

    for column in columns:
        normalized = normalize_name(column)

        if normalized in possible_names:
            return column

    return None


