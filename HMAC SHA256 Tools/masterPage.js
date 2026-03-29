// The code in this file will load on every page of your site

import {hmacSHA256hex} from 'public/hmacSHA256.js';
import {hmacSHA256base64} from 'public/hmacSHA256.js';

$w.onReady(function () {
	console.log(hmacSHA256hex('acdac7141bd698153117ea6c5dd5574ad937b685', 'nomis'));
	console.log(hmacSHA256base64('acdac7141bd698153117ea6c5dd5574ad937b685', 'nomis'));
});