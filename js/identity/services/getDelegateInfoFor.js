const algosdk = require("algosdk");
const client = require("../algoClient");

const getDelegateInfoFor = async (accountAddress, delegateAddress, appID) => {
  if (
    !(
      algosdk.isValidAddress(accountAddress) &&
      algosdk.isValidAddress(delegateAddress)
    )
  ) {
    throw new Error(`Invalid algo address ${accountAddress}`);
  }

  const accountInfo = await client.accountInformation(accountAddress).do();

  const createdApps = accountInfo["apps-local-state"] || [];
  const identityAppLocalState = createdApps.find((app) => app.id === appID);

  if (identityAppLocalState.length === 0) {
    throw Error("local state for app not found");
  }

  const base64Address = Buffer.from(delegateAddress).toString("base64");
  const delegateData = identityAppLocalState["key-value"].find(
    (keyVals) => keyVals.key == base64Address
  );

  const buffer = Buffer.from(delegateData.value.bytes, "base64");
  const [expireAt, role] = algosdk.decodeObj(buffer);

  return {
    address: delegateAddress,
    expireAt,
    role,
  };
};

module.exports = getDelegateInfoFor;
