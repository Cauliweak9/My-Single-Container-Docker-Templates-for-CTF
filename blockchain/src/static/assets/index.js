import { ethers } from "./ethers.min.js";
import { provider } from "./config.js";

async function startEnvironment() {
    const signer = await provider.getSigner();
    console.log(signer);
}

async function createNewInstance() {

}

async function submitInstance() {

}