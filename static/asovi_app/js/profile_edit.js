'use strict';
 function previewImage(obj) {
   var fileReader = new FileReader();
   fileReader.onload = (function(){
     document.getElementById('sampleimg').src = fileReader.result;
   });
   fileReader.readAsDataURL(obj.files[0]);
 }


 
