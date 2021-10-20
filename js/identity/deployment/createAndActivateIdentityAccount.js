const util = require("./util");
const createPaymentTransaction = require("../services/createPaymentTransaction");

const createAndActivateIdentityAccount = async (
  client,
  sender,
  amount = 1000000,
  activate = true 
) => {
  const logicSignatureAccount = await util.createLogicSignatureAccount(
    client,
    "../contracts/teal/identity_account.teal"
  );

  console.log("Logic Signature Address:", logicSignatureAccount.address());

  if (activate) {
    await createPaymentTransaction(client, sender, logicSignatureAccount.address(), amount);
  }

  return logicSignatureAccount;
};

module.exports = createAndActivateIdentityAccount;