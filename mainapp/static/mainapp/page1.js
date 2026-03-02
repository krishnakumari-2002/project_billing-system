function addProduct() {
    const div = document.createElement("div");
    div.classList.add("product-row");

    div.innerHTML = `
        <input type="number" class="product_id" placeholder="Product ID">
        <input type="number" class="quantity" placeholder="Quantity">
        <button type="button" class="remove-btn" onclick="this.parentElement.remove()">Remove</button>
    `;

    document.getElementById("productContainer").appendChild(div);
}