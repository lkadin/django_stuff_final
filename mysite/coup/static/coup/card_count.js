function checkboxlimit(checkgroup, limit){
	var checkgroup=checkgroup;
	var limit=limit;
	var checkedcount=0;
	for (var i=0; i<checkgroup.length; i++) {
		checkedcount += (checkgroup[i].checked)? 1 : 0;
	}
	if (checkedcount !== limit){
		alert("You must select " + limit + " checkboxes");
		return false;
	}
}

