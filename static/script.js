$(".quantity").on("input", function (event) {
  let symbol = event.target.id;
  let quantity = event.target.value;
  let price = $(`#${symbol}-price`).val();
  let total = $(`#${symbol}-hiddenTotal`).val();
  let stockTotal = stockMath(quantity, price);
  console.log(`total: ${total}; stockTotal: ${stockTotal}`);
  let newTotal = Math.floor((stockTotal - total) * 100) / 100;
  console.log(newTotal);
  let cash = $("#dollars").val();
  let dollars =
  Math.floor((cash - newTotal) * 100) / 100;
  if (dollars < 0){
    amount = $(`#${symbol}`).val();
    $(`#${symbol}`).val(amount - 1);
    return window.alert("Cash cannot be less than zero");
  }
  $(`#${symbol}-hiddenTotal`).val(stockTotal);
  $(`#${symbol}-total`).text(`$${stockTotal}`);
  $("#dollars").val(dollars);
  $("#cash").text(`Cash: $${dollars}`);
  return dollars;
});

function stockMath(quantity, price) {
  let total = Math.floor(quantity * price * 100) / 100;
  
  return total;
}
