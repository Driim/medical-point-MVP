class UserService:
    async def have_read_access(self, user_id: str, organization_id: str) -> bool:
        # TODO: implement
        return True

    async def have_write_access(self, user_id: str, organization_id: str) -> bool:
        # TODO: implement
        return True

    async def get_available_organization_units(self, user_id: str) -> list[str]:
        return ["33b8b452-00cf-42f7-8f4b-ce867c68b8c1"]
