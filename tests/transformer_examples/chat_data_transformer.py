def transform(src, dst):
    dst.messages[0] = src.observations[0].input[0]
    if src.observations[0].output.content.lower() == 'yes':
        dst.messages[1] = src.observations[0].output['role', 'content']