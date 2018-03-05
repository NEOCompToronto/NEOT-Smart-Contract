from nex.common.storage import StorageAPI

class Token():

    name = 'NEOT'
    symbol = 'NCT'
    decimals = 8

    owner = b'\x15\xb2V\xb8\xe5\x1bi\xfb\xf9\xfbmb\x8d\xa8\x14\x8b\xbf^\xfey'
    in_circulation_key = b'in_circulation'

    total_supply = 10000000 * 100000000
    initial_amount = 2500000 * 100000000
    tokens_per_neo = 40 * 100000000
    tokens_per_gas = 20 * 100000000
    max_exchange_limited_round = 50000 * 40 * 100000000

    block_sale_start = 1
    limited_round_end = 1 + 1000000

    def crowdsale_available_amount(self):
        storage = StorageAPI()
        in_circ = storage.get(self.in_circulation_key)
        available = self.total_supply - in_circ
        return available


    def add_to_circulation(self, amount:int, storage:StorageAPI):
        current_supply = storage.get(self.in_circulation_key)
        current_supply += amount
        storage.put(self.in_circulation_key, current_supply)

    def get_circulation(self, storage:StorageAPI):
        return storage.get(self.in_circulation_key)

