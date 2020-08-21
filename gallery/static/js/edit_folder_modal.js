Window.modal_data = {}
var select_type=document.getElementById('selectType');
var select_category = document.getElementById("selectCategory");
var input_type_name=document.getElementById('input-type-name');
var input_category_name=document.getElementById('input-category-name');

String.prototype.replaceAll = function(search, replace){
    return this.split(search).join(replace);
}

function fill_categories_list(raw_categories){
    var selected_type=select_type.value;
    var all_categories = JSON.parse(raw_categories.replaceAll("&#34;", "\""));

    var categories = all_categories[selected_type];
    select_category.querySelectorAll('*').forEach(n => n.remove());
    
    var categories_count = categories.length;
    
    if (categories_count <= 0){
        select_category.disabled = true;
        return;
    } else {
        select_category.disabled = false;
    }

    var el = document.createElement("option");
    el.text = 'You can select here';
    el.value = '';

    select_category.add(el);

    for(var i = 0; i < categories.length; i++) {
        var opt = categories[i];
        var el = document.createElement("option");
        el.text = opt;
        el.value = opt;
        select_category.add(el);
    }
    if (Window.selected_category != "None"){
        select_category.value = Window.selected_category;
    }
}

function show_modal(uid, type, category){
    var txt = document.createTextNode(uid);
    var folder_name_label = document.getElementById('folder-name-label')
    if (folder_name_label.hasChildNodes()) {
        folder_name_label.replaceChild(txt, folder_name_label.firstChild);
    } else {
        folder_name_label.appendChild(txt);
    }
    document.getElementById('catalog_id-input').value=uid;
    select_type.value = type
    Window.selected_category = category
    if ( typeof type != "undefined"){
        fill_categories_list(Window.categories_by_type);
    }
    MicroModal.show('modal-edit-folder');
}

select_type.onchange = function(){
    fill_categories_list(Window.categories_by_type);
}

input_type_name.oninput = function(){
    var content=input_type_name.value;
    var old_selections_disabled = content.length>0;
    select_type.disabled = old_selections_disabled;
    select_category.disabled = old_selections_disabled;
}

input_category_name.oninput = function(){
    var content=input_category_name.value;
    select_category.disabled = content.length>0;
}
