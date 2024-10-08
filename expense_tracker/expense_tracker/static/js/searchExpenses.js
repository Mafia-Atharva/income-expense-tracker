const searchField=document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output");
const appTable=document.querySelector(".app-table")
const paginationContainer=document.querySelector(".pagination-container")
const tbody= document.querySelector(".table-body")
const noResults=document.querySelector(".no-results")


tableOutput.style.display="none";


searchField.addEventListener('keyup', (e)=>{

    const searchValue=e.target.value;

    if(searchValue.trim().length>0){
        paginationContainer.style.display="none";
        tbody.innerHTML="";
        fetch("/search-expenses/", {
            body: JSON.stringify({ seachText: searchValue }),
            method: "POST",
        }).then((res) => res.json()).then((data) => {
            appTable.style.display="none";
            tableOutput.style.display="block";
            if(data.length===0){
                tableOutput.style.display="none";
                noResults.style.display="block"
            }else{
                noResults.style.display="none";
                tableOutput.style.display="block"
                data.forEach(item => {
                    
                    tbody.innerHTML+=`
                    <tr>
                    <td class="text-center">${item.amount}</td>
                    <td class="text-center">${item.category}</td>
                    <td class="text-center">${item.description}</td>
                    <td class="text-center">${item.date}</td>
                    </tr>
                    
                    `
                });
                
            }
        });

    }else{
        appTable.style.display="block";
        paginationContainer.style.display="block";
        tableOutput.style.display="none";
    }

})