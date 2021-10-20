const algosdk = require("algosdk");
const client = require("./algoClient");
const config = require("./config");
const deployIdentityContract = require("./deployment/deployIdentityContract");
const createAndActivateIdentityAccount = require("./deployment/createAndActivateIdentityAccount");
const createAddDelegateTransaction = require("./services/createAddDelegateTransaction");
const getDelegateInfoFor = require("./services/getDelegateInfoFor");
const createRemoveDelegateTransaction = require("./services/createRemoveDelegateTransaction");
const createOptInTransaction = require("./services/createOptInAppTransaction");
const passPhrase = config.get("algorand.wallets.wallet4.nmonic");

const sender = algosdk.mnemonicToSecretKey(passPhrase);

const getExpirationBlock = () => {
  const futureTrxDate = "01 January 2022 17:20 UTC";
  const a = new Date(futureTrxDate);
  const b = new Date();

  const diff_seconds = Math.abs(Math.round((+b - +a) / 1000));
  const blockRound = Math.abs(Math.round(diff_seconds / 4.5));

  return blockRound;
};

(async () => {
  // const tx = await deployIdentityContract(client, sender);
  // console.log("tx----deployed", tx);
  // const applicationID = tx["application-index"];
  const applicationID = 39004555;

  console.log("-------- deployed identity smart contract --------");
  const identityLogicSignatureAccount = await createAndActivateIdentityAccount(
    client,
    sender,
    1000000,
    false
  );
  console.log("********** activated identity account **********");

  // const optInTransaction = await createOptInTransaction(
  //   client,
  //   identityLogicSignatureAccount,
  //   applicationID
  // );
  //
  console.log("-------- opted-in identity account --------");

  // console.log("optInTransaction", optInTransaction); //XHJEJW6EBGFN6H45P7XI6ODOIKQMB7G3TFSSMIL7M6HITJDE5DCA

  const expireAt = getExpirationBlock();
  const delegateAddress =
    "4AFMHWI2GZUPRRWUNBHKV7ANFKLIMJ5G6VIOBXF4YF7TUDMH3ZY22QTR7Q";

  const role = 1;

  const addDelegateTx = await createAddDelegateTransaction(
    client,
    identityLogicSignatureAccount,
    applicationID,
    delegateAddress,
    expireAt,
    role
  );

  console.log("addDelegateTx", addDelegateTx);

  // const removeAddDelegate = await createRemoveDelegateTransaction(
  //   client,
  //   identityLogicSignatureAccount,
  //   applicationID,
  //   delegateAddress,
  // )

  // console.log("removeAddDelegate", removeAddDelegate);

  const delegateData = await getDelegateInfoFor(
    "5QWQ3DPBFLTOT64LVXBRL2SDL7ESJD2WTRURRGXK5GHPIOOJQCENC3AOUA",
    "4AFMHWI2GZUPRRWUNBHKV7ANFKLIMJ5G6VIOBXF4YF7TUDMH3ZY22QTR7Q",
    39004555
  );
  console.log("delegateData", delegateData);
})();
