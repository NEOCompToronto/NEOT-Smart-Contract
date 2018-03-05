from boa.blockchain.vm.Neo.Blockchain import GetHeight
from boa.blockchain.vm.Neo.Action import RegisterAction
from boa.blockchain.vm.Neo.Runtime import Notify,CheckWitness
from boa.code.builtins import concat
from neot.token.mytoken import Token
from nex.common.storage import StorageAPI
from nex.common.txio import Attachments,get_asset_attachments

OnTransfer = RegisterAction('transfer', 'from', 'to', 'amount')
OnRefund = RegisterAction('refund', 'to', 'amount')

OnInvalidKYCAddress = RegisterAction('invalid_registration','address')
OnKYCRegister = RegisterAction('kyc_registration','address')


class Crowdsale():

    kyc_key = b'kyc_ok'

    limited_round_key = b'r1'


    def kyc_register(self, args, token:Token):

        ok_count = 0

        if CheckWitness(token.owner):

            for address in args:

                if len(address) == 20:

                    storage = StorageAPI()

                    kyc_storage_key = concat(self.kyc_key, address)
                    storage.put(kyc_storage_key, True)

                    OnKYCRegister(address)
                    ok_count += 1

        return ok_count


    def kyc_status(self, args):

        storage = StorageAPI()

        if len(args) > 0:
            addr = args[0]

            kyc_storage_key = concat(self.kyc_key, addr)

            return storage.get(kyc_storage_key)

        return False



    def exchange(self, token: Token):

        attachments = get_asset_attachments()

        storage = StorageAPI()

        can_exchange = self.can_exchange(token, attachments, storage, False)

        if not can_exchange:
            print("Cannot exchange value")

            if attachments.neo_attached > 0:
                OnRefund(attachments.sender_addr, attachments.neo_attached)

        return False


        current_balance = storage.get(attachments.sender_addr)

        exchanged_tokens = attachments.neo_attached * token.tokens_per_neo / 100000000

        new_total = exchanged_tokens + current_balance
        storage.put(attachments.sender_addr, new_total)

        token.add_to_circulation(exchanged_tokens, storage)

        OnTransfer(attachments.receiver_addr, attachments.sender_addr, exchanged_tokens)

        return True


    def can_exchange(self, token:Token, attachments:Attachments, storage:StorageAPI, verify_only: bool) -> bool:

        if attachments.neo_attached == 0:
            return False

        if not self.get_kyc_status(attachments.sender_addr, storage):
            return False

        amount_requested = attachments.neo_attached * token.tokens_per_neo / 100000000

        can_exchange = self.calculate_can_exchange(token, amount_requested, attachments.sender_addr, verify_only)

        return can_exchange


    def get_kyc_status(self, address, storage:StorageAPI):

        kyc_storage_key = concat(self.kyc_key, address)

        return storage.get(kyc_storage_key)


    def calculate_can_exchange(self, token: Token, amount: int, address, verify_only: bool):

        height = GetHeight()

        storage = StorageAPI()

        current_in_circulation = storage.get(token.in_circulation_key)

        new_amount = current_in_circulation + amount

        if new_amount > token.total_supply:
            print("amount greater than total supply")
            return False

        print("trying to calculate height????")
        if height < token.block_sale_start:
            print("sale not begun yet")
            return False

        if height > token.limited_round_end:
            print("Free for all, accept as much as possible")
            return True


        if amount <= token.max_exchange_limited_round:

            r1key = concat(address, self.limited_round_key)

            has_exchanged = storage.get(r1key)

            if not has_exchanged:
                if not verify_only:
                    storage.put(r1key, True)
                return True

            print("already exchanged in limited round")
            return False

        print("too much for limited round")

        return False
