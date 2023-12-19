from typing import Any

from tackle import Context, DocumentValueType
from tackle.parser import walk_document


def f(context: Context, items: DocumentValueType) -> Any:
    tmp_context = Context(
        verbose=context.verbose,
        no_input=context.no_input,
        key_path=context.key_path.copy(),
        key_path_block=context.key_path.copy(),
        path=context.path,
        data=context.data,
        hooks=context.hooks,
        source=context.source,
    )

    walk_document(context=tmp_context, value=items)

    return tmp_context.data.public
