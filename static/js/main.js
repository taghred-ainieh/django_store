async function cartupdate(element ) {
    const {data}=await axios(element.dataset.url)
    const{message,items_count}=data
    notyf.success({
        message,
        dismissible:true,
        icon:false
    })
    document.getElementById('cart-items-count').innerHTML=items_count
}




async function cartremove(element ) {
    await axios(element .dataset.url)
    location.reload()
    
}