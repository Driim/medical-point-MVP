def update_model_by_dto(model, dto: dict[str, any]):
    for key, value in dto.items():
        setattr(model, key, value)
