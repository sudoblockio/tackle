from tackle import BaseHook, Context


def init_context(self: BaseHook, context: 'Context'):
    # Update the render_context that will be used
    if self.render_context is not None:
        return

    # fmt: off
    existing = context.data.existing if context.data.existing is not None else {}
    temporary = context.data.temporary if context.data.temporary is not None else {}
    private = context.data.private if context.data.private is not None else {}
    public = context.data.public if context.data.public is not None else {}
    # fmt: on

    self.render_context = {
        **existing,
        **temporary,
        **private,
        **public,
    }

    if self.extra_context is not None:
        if isinstance(self.extra_context, list):
            for i in self.extra_context:
                self.render_context.update(i)
        else:
            self.render_context.update(self.extra_context)
