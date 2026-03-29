
export function hmacSHA256hex(productID,password){
	var CryptoJS = require("crypto-js");
	var ciphertextHex = CryptoJS.HmacSHA256('acdac7141bd698153117ea6c5dd5574ad937b685', 'nomis');
	return ciphertextHex.toString();
}

export function hmacSHA256base64(productID,password){
	var CryptoJS = require("crypto-js");
	var Base64 = require("crypto-js/enc-base64");
	
	const ciphertextBase64 = Base64.stringify(CryptoJS.HmacSHA256('acdac7141bd698153117ea6c5dd5574ad937b685', 'nomis'));
	return ciphertextBase64.toString();

}