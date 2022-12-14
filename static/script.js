$(".quantity").on("input", function (event) {
  let symbol = event.target.id;
  let quantity = event.target.value;
  let price = $(`#${symbol}-price`).val();
  console.log(price);
  let total = $(`#${symbol}-hiddenTotal`).val();
  let stockTotal = stockMath(symbol, quantity, price);
  let newTotal = stockTotal - total;
  let cash = $("#dollars").val();
  let dollars = Math.floor((cash - newTotal) * 100) / 100;
  return $("#dollars").val(dollars);
});

function stockMath(symbol, quantity, price) {
  let total = Math.floor(quantity * price * 100) / 100;
  $(`#${symbol}-hiddenTotal`).val(total);
  $(`#${symbol}-total`).html(`Total: ${total}`);
  return total;
}
