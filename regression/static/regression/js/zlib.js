 function zlibDecompress(base64Content){
    var strData     = atob(base64Content);
    var charData    = strData.split('').map(function(x){return x.charCodeAt(0);});
    var binData     = new Uint8Array(charData);
    var data        = pako.inflate(binData, { to: 'string' });
    return data;
}