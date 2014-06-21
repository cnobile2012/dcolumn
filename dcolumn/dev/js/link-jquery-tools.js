/*
 * Attach utility methods to the element tags that want them.
 */
$(document).ready(function() {
  /* Add the datepicker to every control that wants it. */
  $('.wants_datepicker').each(function(index) {
    // Save the current value then place it into the datepicker.
    var default_value = $(this).val();

    if(default_value) {
      // Convert it from an ISO-formatted string into a Date object.
      default_value = $.datepicker.parseDate('yy-mm-dd', default_value);
    }

    $(this).datepicker();
    $(this).datepicker('option', 'dateFormat', 'd MM, yy');

    if(default_value) {
      $(this).datepicker('setDate', default_value);
    }
  });

  /* Add autocomplete to every control that wants it. MAY NOT BE USED */
  $('.wants_autocomplete').each(function(index) {
    // Save the current value then place it into the combobox.
    var value = $(this).val();
    $(this).combobox();
    $(this).combobox('value', value);
  });
});
