import { ethers } from "ethers";
import fs from "fs";
import path from "path";
import { stringify } from "csv-stringify";

// Replace with a Flare network RPC URL
const FLARE_RPC_URL = "https://flare-api.flare.network/ext/bc/C/rpc";
const NUM = 50000

async function getWalletAddressesFromLatestBlock() {
    try {
        const provider = new ethers.JsonRpcProvider(FLARE_RPC_URL);
        
        // Get latest block number
        const blockNumber = await provider.getBlockNumber();

        const walletAddresses = new Set();
        var counter = 1
        var size = 0

        while (size < NUM){
        
            // Get the latest block details (with transaction hashes)
            const block = await provider.getBlock(blockNumber - counter);
            counter += 100;

            if (!block || !block.transactions) {
                console.log("No transactions found in the latest block.");
                return;
            }
        
            // Extract unique wallet addresses from the transactions
            for (const txHash of block.transactions) {
                // Fetch the full transaction details using the transaction hash
                const tx = await provider.getTransaction(txHash);
                if (tx.from){
                    walletAddresses.add(tx.from);  // Add sender address if present
                    size += 1;
                    if (size % 100 == 0) console.log(size);
                }
                if (tx.to){
                    walletAddresses.add(tx.to);      // Add recipient address if present
                    size += 1;
                    if (size % 100 == 0) console.log(size);
                }
            }
        }
        // Convert to CSV format
        stringify(Array.from(walletAddresses).map(addr => [addr]), { header: true, columns: ["Wallet Address"] }, (err, csvData) => {
            if (err) {
                console.error("Error generating CSV:", err);
                return;
            }
            
            // Define file path
            const filePath = path.join(process.cwd(), "wallet_addresses.csv");
            
            // Write to CSV file
            fs.writeFileSync(filePath, csvData);
            console.log("Wallet addresses have been saved to:", filePath);
        });

    } catch (error) {
        console.error("Error fetching block data:", error);
    }
}
getWalletAddressesFromLatestBlock();