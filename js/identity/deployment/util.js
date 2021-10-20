const algosdk = require("algosdk");
const fs = require("fs");
const path = require("path");

const getProgramBytes = async (client, filePath) => {
  const approvalPath = path.join(__dirname, filePath);
  const program = fs.readFileSync(approvalPath);

  const compiledProgram = await client.compile(program).do();
  return new Uint8Array(Buffer.from(compiledProgram.result, "base64"));
};

const createLogicSignatureAccount = async (client, filePath) => {
  const program = await getProgramBytes(client, filePath);

  const logicSignature = new algosdk.LogicSigAccount(program);

  return logicSignature;
};

const runPython = async (filePath) => {
  const { spawn } = require("child_process");
  const pyprog = spawn("python3", [path.join(__dirname, filePath)]);

  let data = "";
  for await (const chunk of pyprog.stdout) {
    console.log("stdout chunk: " + chunk);
    data += chunk;
  }

  let error = "";
  for await (const chunk of pyprog.stderr) {
    console.error("stderr chunk: " + chunk);
    error += chunk;
  }

  const exitCode = await new Promise((resolve, reject) => {
    pyprog.on("close", resolve);
  });

  if (exitCode) {
    throw new Error(`subprocess error exit ${exitCode}, ${error}`);
  }
  return data;
};

module.exports = {
  getProgramBytes,
  createLogicSignatureAccount,
  runPython,
};
