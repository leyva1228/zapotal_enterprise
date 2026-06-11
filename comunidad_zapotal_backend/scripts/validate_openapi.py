"""
Script para validar el schema OpenAPI generado.
"""
import json
import sys
from pathlib import Path


def validate_schema(schema_path: str = 'schema.json') -> bool:
    """
    Valida que el schema OpenAPI tenga la estructura básica requerida.

    Returns:
        True si el schema es válido
    """
    path = Path(schema_path)

    if not path.exists():
        print(f'❌ Schema file not found: {schema_path}')
        return False

    try:
        with open(path) as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        print(f'❌ Invalid JSON: {e}')
        return False

    # Validar OpenAPI 3.x
    if 'openapi' not in schema:
        print('❌ Missing "openapi" key')
        return False

    if not schema['openapi'].startswith('3.'):
        print(f'❌ Not OpenAPI 3.x: {schema["openapi"]}')
        return False

    # Validar paths
    paths = schema.get('paths', {})
    if not paths:
        print('❌ No paths defined')
        return False

    print(f'✅ OpenAPI version: {schema["openapi"]}')
    print(f'✅ Total paths: {len(paths)}')

    # Verificar que cada path tiene métodos y responses
    errors = []
    for path, methods in paths.items():
        for method, spec in methods.items():
            if method.startswith('x-'):
                continue
            if 'responses' not in spec:
                errors.append(f'{method.upper()} {path}: sin responses')

    if errors:
        print(f'\n⚠️  Warnings ({len(errors)}):')
        for err in errors[:10]:
            print(f'   - {err}')
        if len(errors) > 10:
            print(f'   ... y {len(errors) - 10} más')

    # Verificar que no se expongan passwords
    password_exposed = []
    components = schema.get('components', {}).get('schemas', {})
    for schema_name, schema_def in components.items():
        props = schema_def.get('properties', {})
        if 'password' in props:
            password_field = props['password']
            # write_only debe ser True
            if not password_field.get('writeOnly', False):
                password_exposed.append(schema_name)

    if password_exposed:
        print(f'\n❌ Passwords exposed in: {password_exposed}')
        return False

    # Verificar que haya security definitions
    if 'securitySchemes' not in schema.get('components', {}):
        print('\n⚠️  No security schemes defined')

    print('\n✅ Schema validation passed')
    return True


if __name__ == '__main__':
    schema_file = sys.argv[1] if len(sys.argv) > 1 else 'schema.json'
    success = validate_schema(schema_file)
    sys.exit(0 if success else 1)
