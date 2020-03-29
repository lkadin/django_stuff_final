function CheckBoxCount() {
var inputList=document.getElementsByTagName("input");
var numChecked=0;

for (var i=0; i < inputList.length; i++) {
    if (inputList[i].type == "checkbox" && inputList[i].checked) {
    numChecked = numChecked + 1;
        }
    }
return true;

}


function checkboxlimit(checkgroup, limit){
	var checkgroup=checkgroup
	var limit=limit
	for (var i=0; i<checkgroup.length; i++){
		checkgroup[i].onclick=function(){
		var checkedcount=0
		for (var i=0; i<checkgroup.length; i++)
			checkedcount+=(checkgroup[i].checked)? 1 : 0
		if (checkedcount>limit){
			alert("You can only select a maximum of "+limit+" checkboxes")
			this.checked=false
			}
		}
	}
}