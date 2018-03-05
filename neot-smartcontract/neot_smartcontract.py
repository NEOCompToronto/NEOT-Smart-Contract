from boa.blockchain.vm.Neo.Runtime import GetTrigger, CheckWitness, Notify
from boa.blockchain.vm.Neo.TriggerType import Application, Verification
from nex.common.storage import StorageAPI
from nex.common.txio import Attachments,get_asset_attachments
from neot.token.mytoken import Token
from neot.token.nep5 import NEP5Handler
from neot.token.crowdsale import Crowdsale


def Main(operation, args):
    trigger = GetTrigger()
    token = Token()

    if trigger == Verification:

        is_owner = CheckWitness(token.owner)
        if is_owner:
            return True

        attachments = get_asset_attachments()
        storage = StorageAPI()
        crowdsale = Crowdsale()

        return crowdsale.can_exchange(token, attachments, storage, True)

    elif trigger == Application:

        if operation != None:
            nep = NEP5Handler()

            for op in nep.get_methods():
                if operation == op:
                    return nep.handle_nep51(operation, args, token)

            if operation == 'deploy':
                return deploy(token)

            if operation == 'circulation':
                storage = StorageAPI()
                return token.get_circulation(storage)

            sale = Crowdsale()

            if operation == 'mintTokens':
                return sale.exchange(token)

            if operation == 'crowdsale_register':
                return sale.kyc_register(args, token)

            if operation == 'crowdsale_status':
                return sale.kyc_status(args)

            if operation == 'crowdsale_available':
                return token.crowdsale_available_amount()

            return 'unknown operation'

    return False


def deploy(token: Token):

    if not CheckWitness(token.owner):
        print("Must be owner to deploy")
        return False

    storage = StorageAPI()

    if not storage.get('initialized'):
        storage.put('initialized', 1)
        storage.put(token.owner, token.initial_amount)
        token.add_to_circulation(token.initial_amount, storage)
        return True

    return False



