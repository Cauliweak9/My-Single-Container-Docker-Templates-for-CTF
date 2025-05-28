import { ethers } from "./ethers.min.js";

const RPC_URL = "http://127.0.0.1:8545";
export const provider = new ethers.JsonRpcProvider(RPC_URL);