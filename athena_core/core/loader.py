from athena_core.core.registry import REGISTERED_MODULES

def list_modules():
    modules = []

    for module_id, info in REGISTERED_MODULES.items():
        path = info['path']
        modules.append({
            'id': module_id,
            'name': info['name'],
            'status': info['status'],
            'version': info['version'],
            'exists': path.exists(),
            'path': str(path)
        })

    return modules


def print_modules():
    print('ATHENA CORE - MODULE REGISTRY')
    print('-' * 40)

    for module in list_modules():
        exists_label = 'OK' if module['exists'] else 'PENDING'
        print(f"{module['id']} | {module['name']} | {module['status']} | {exists_label}")


if __name__ == '__main__':
    print_modules()
