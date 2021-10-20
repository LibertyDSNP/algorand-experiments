const { runPython } = require("./util");
const path = require("path");

(async () => {
  await runPython("../contracts/identity_smart_contract.py");
  console.log("compiled to Teal: identity_smart_contract")
  await runPython("../contracts/identity_account.py");
  console.log("compiled to Teal: identity_account")
})();
