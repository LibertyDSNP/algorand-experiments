const algosdk = require("algosdk");
const getDelegateInfoFor = require("./services/getDelegateInfoFor");
const algoClient = require("./algoClient");

const ecodeAddress = algosdk.encodeAddress(
  new Uint8Array(
    Buffer.from("5QWQ3DPBFLTOT64LVXBRL2SDL7ESJD2WTRURRGXK5GHPIOOJQCENC3AOUA")
  )
);
console.log({ ecodeAddress });
const decode = algosdk.decodeAddress(
  "5QWQ3DPBFLTOT64LVXBRL2SDL7ESJD2WTRURRGXK5GHPIOOJQCENC3AOUA"
);
console.log({ decode });

const encodeObj = algosdk.encodeObj({ taco: 1 });
console.log(encodeObj);

const decodeObj = algosdk.decodeObj(encodeObj);
console.log("decodeObj", decodeObj);

console.log(algosdk.encodeUint64(1));

(async () => {
  const delegateData = await getDelegateInfoFor(
    "5QWQ3DPBFLTOT64LVXBRL2SDL7ESJD2WTRURRGXK5GHPIOOJQCENC3AOUA",
    "4AFMHWI2GZUPRRWUNBHKV7ANFKLIMJ5G6VIOBXF4YF7TUDMH3ZY22QTR7Q",
    39004555
  );

  console.log("delegateData", delegateData);

  const appID = 38451660;

  const applicationInfo = await algoClient.getApplicationByID(appID).do();
  console.log("applicationInfo", applicationInfo);
})();
