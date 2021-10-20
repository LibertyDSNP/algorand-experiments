let client = require("../algoClient");

// NOT USED FOR ANYTHING JUST EXPLORING
const getAppStateFromAccount = async (accountAdress, appID) => {
  const accountInfo = await client.accountInformation(accountAdress).do();
  const applicationInfo = await client.getApplicationByID(appID).do();
  console.log("accountinfo", accountInfo);
  console.log("applicationInfo", applicationInfo);

  const createdApps = accountInfo["created-apps"];

  const counterApp = createdApps.find((app) => app.id === appID);

  console.log("counterApp", counterApp);

  const globalState = counterApp.params["global-state"];
  console.log("globalState", globalState);

  console.log("state.key", globalState[0].key);

  const buff = Buffer.from(globalState[0].key, "base64");

  const text = buff.toString("ascii");
  console.log("text", text);
};

module.exports = getAppStateFromAccount;
