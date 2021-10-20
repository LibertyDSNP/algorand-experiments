const algosdk = require("algosdk");
const utils = require("../utils/utils");
const fs = require("fs");
const path = require("path");

const algodToken =
  "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const algodServer = "http://localhost";
const algodPort = 4001;

const passPhrase =
  "amount oval fabric pave tip stand essay apart galaxy embark invite become bracket maximum innocent horror pelican cage eager sing uniform material cereal ability bottom";

let client = new algosdk.Algodv2(algodToken, algodServer, algodPort);

const sender = algosdk.mnemonicToSecretKey(passPhrase);


(async () => {
  const getSmartSignatureProgramBytes = async (client) => {
    const approvalPath = path.join(__dirname, "./teal/sample_smart_sig.teal");
    const program = fs.readFileSync(approvalPath);

    // use algod to compile the program
    const compiledProgram = await client.compile(program).do();
    return new Uint8Array(Buffer.from(compiledProgram.result, "base64"));
  };

  const paymentTransaction = async (sender, receiver, amount) => {
    console.log("sender", sender.addr);

    // provide the default values that are required to submit a transaction, such as the expected fee for the transaction
    const suggestedParams = await client.getTransactionParams().do();

    const unsignedPaymentTxn = algosdk.makePaymentTxnWithSuggestedParams(
      sender.addr,
      receiver,
      amount,
      undefined,
      new Uint8Array(0),
      suggestedParams
    );

    const signedCreatePaymentTxn = unsignedPaymentTxn.signTxn(sender.sk);

    const { txId: createTxId } = await client
      .sendRawTransaction(signedCreatePaymentTxn)
      .do();

    const completedTx = await utils.verboseWaitForConfirmation(
      client,
      createTxId
    );

    return completedTx;
  };

  const createLogicSignatureAccount = async () => {
    const program = await getSmartSignatureProgramBytes(client);

    const logicSignature = new algosdk.LogicSigAccount(program);

    return logicSignature;
  };

  // The primary difference is that the function is passed the base64 encoded string of the compiled bytecode for the smart signature and the escrow’s Algorand address.
  // The program is then converted to a byte array and the Python SDK’s LogicSig function is used to create a logic signature from the program bytes.
  const logicSignaturePaymentTxn = async () => {
      // 1. compile stateless program 
      // 2. activate s.s by sending algos to it
      //    paymentTxt(sender, amount, address_of_sm,)
      // 3. createLogicSign(program, address, receiver)
    const receiver =
      "NZHJVFZNVQGCKVMSHZC2QCB22EO7CU6ZXPH3XFRS5RENGVLUTI2K3J2ALA";
    // const receiver = "MS5OMYMTMWO7VM4CU4LMQRWN7YL2P7ZY45AX2OKP2LAUEZUWEV2SIZLVDE"
    const amount = 10000;
    // provide the default values that are required to submit a transaction, such as the expected fee for the transaction

    const logicSignatureAccount = await createLogicSignatureAccount();
    console.log("Logic Signature Address:", logicSignatureAccount.address());

    const suggestedParams = await client.getTransactionParams().do();

    const signPaymentTxn = await paymentTransaction(sender, logicSignatureAccount.address(), 1000000)

    const unsignedPaymentTxn =
      algosdk.makePaymentTxnWithSuggestedParamsFromObject({
        from: logicSignatureAccount.address(),
        to: receiver,
        amount,
        suggestedParams,
      });

    const signedLogicSignature = algosdk.signLogicSigTransactionObject(
      unsignedPaymentTxn,
      logicSignatureAccount
    );

    console.log("signedLogicSignature", signedLogicSignature);

    try {
      const { txId: createTxId } = await client
        .sendRawTransaction(signedLogicSignature.blob)
        .do();

      const completedTx = await utils.verboseWaitForConfirmation(
        client,
        createTxId
      );

      return completedTx;
    } catch (e) {
      console.log("error:", e);
    }
  };

  const tx = await logicSignaturePaymentTxn();
  //   const tx = await paymentTransaction(
  //     sender,
  //     "MS5OMYMTMWO7VM4CU4LMQRWN7YL2P7ZY45AX2OKP2LAUEZUWEV2SIZLVDE",
  //     10000
  //   );

  console.log("tx", tx);
})();
