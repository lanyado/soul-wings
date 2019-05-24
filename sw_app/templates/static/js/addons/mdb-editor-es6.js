($ => {

  $.fn.mdbEditor = function () {

    return this.map((i, e) => {

      let $selectedRow,
        $selectedTable = $(e),
        $selectedTableId = $selectedTable.closest('.wrapper-modal-editor').find('table').attr('id'),
        $selectedTableSharp = $(`#${$selectedTableId}`),
        $table = $(`#${$selectedTableId}`).DataTable(),
        $wrapperModalEditor = $selectedTableSharp.closest('.wrapper-modal-editor'),
        $createShowP = $wrapperModalEditor.find('.createShowP'),
        $buttonEdit = $wrapperModalEditor.find('.buttonEdit'),
        $buttonDelete = $wrapperModalEditor.find('.buttonDelete'),
        $buttonAddFormWrapper = $wrapperModalEditor.find('.buttonAddFormWrapper'),
        $buttonEditWrapper = $wrapperModalEditor.find('.buttonEditWrapper'),
        $editInsideWrapper = $wrapperModalEditor.find('.editInsideWrapper'),
        $deleteButtonsWrapper = $wrapperModalEditor.find('.deleteButtonsWrapper'),
        editInside = $wrapperModalEditor.find('.editInside'),
        trColorSelected = '.tr-color-selected';

      const addNewRows = () => {

          let $newRow = [];

          for (let i = 0; i < $wrapperModalEditor.find('.addNewInputs input').length; i++) {

            $newRow.push($wrapperModalEditor.find('.addNewInputs input').eq(i).val());
          }

          $table.row.add($newRow).draw();
        },

        btnToModalAdd = e => {

          let $etargetClosetWrapper = $(e.target).closest('.wrapper-modal-editor');

          $etargetClosetWrapper.find('.addNewInputs input').val('');
          $etargetClosetWrapper.find('.addNewInputs label').removeClass('active');
          $etargetClosetWrapper.find('.addNewInputs input').removeClass('valid');
        },

        addColorToTr = e => $(e.target).parent().not('thead tr').not('tfoot tr').toggleClass('tr-color-selected').siblings().removeClass('tr-color-selected'),

        toggleDisabledToButtons = e => {

          $selectedRow = $(e.target).parent();

          if ($(e.target).parent().not('thead tr').not('tfoot tr').hasClass('tr-color-selected')) {

            $buttonEdit.prop('disabled', false);
            $buttonDelete.prop('disabled', false);
            $createShowP.html('1 row selected');
          } else if (!$('tr').hasClass('tr-color-selected')) {

            $buttonEdit.prop('disabled', true);
            $buttonDelete.prop('disabled', true);
            $createShowP.html('0 row selected');
          }
        },

        buttonEditInput = e => {

          for (let i = 0; i < $(e.target).closest('.wrapper-modal-editor').find('thead tr').children().length; i++) {

            $table.row($wrapperModalEditor.find('.modalEditClass input').eq(i).val($table.cell($selectedRow, i).data()));
          }
        },

        addClassActiveToLabel = () => $('.modalEditClass label').addClass('active'),

        buttonEditInside = e => {

          for (let i = 0; i < $(e.target).closest('.wrapper-modal-editor').find('thead tr').children().length; i++) {

            $table.cell($(trColorSelected).find('td').eq(i)).data($wrapperModalEditor.find('.modalEditClass input').eq(i).val());
          }
        },

        removeColorClassFromTr = () => $selectedTable.find('.tr-color-selected').removeClass('tr-color-selected'),

        disabledButtons = () => {

          $buttonEdit.prop('disabled', true);
          $buttonDelete.prop('disabled', true);
        },

        selectedZeroRowsNews = () => {

          $createShowP.html('0 row selected');
          $table.draw(false);
        },

        buttonDeleteYes = () => {

          $buttonEdit.prop('disabled', true);
          $buttonDelete.prop('disabled', true);
          $createShowP.html('0 row selected');
          $table.row($(trColorSelected)).remove().draw();
        },

        bindEvents = () => {

          $buttonAddFormWrapper.on('click', '.buttonAdd', addNewRows);
          $selectedTableSharp.on('click', 'tr', addColorToTr);
          $selectedTableSharp.on('click', 'tr', toggleDisabledToButtons);
          $buttonEditWrapper.on('click', $buttonEdit, buttonEditInput);
          $buttonEditWrapper.on('click', $buttonEdit, addClassActiveToLabel);
          $deleteButtonsWrapper.on('click', '.btnYesClass', buttonDeleteYes);
          $editInsideWrapper.on('click', editInside, buttonEditInside);
          $editInsideWrapper.on('click', editInside, removeColorClassFromTr);
          $editInsideWrapper.on('click', editInside, disabledButtons);
          $editInsideWrapper.on('click', editInside, selectedZeroRowsNews);
          $('.wrapperToBtnModalAdd').on('click', '.btnToModalAdd', btnToModalAdd);
        };

      bindEvents();
    });
  };

  $.fn.mdbEditorRow = function () {

    return this.map((i, e) => {

      let editRow = '.editRow',
        saveRow = '.saveRow',
        tdLast = 'td:last',
        $removeColumns = $('.removeColumns'),
        $this = $(e),
        $tableId = $this.closest('.wrapper-row-editor').find('table').attr('id'),
        $sharpTableId = $(`#${$tableId}`),
        $tableData = $sharpTableId.DataTable(),
        addNewColumn = '.addNewColumn',
        $buttonWrapper = $('.buttonWrapper'),
        $closeByClick = $('.closeByClick'),
        $showForm = $('.showForm');

      const addNewTr = e => {

          $(document).find($(e.target).parents().eq(1)).map((i, event) => {

            $(event).find('tr').map((i, ev) => {

              $(ev).find(tdLast).not('.td-editor').after('<td class="text-center td-editor" style="border-top: 1px solid #dee2e6; border-bottom:1px solid #dee2e6"><button class="btn btn-sm editRow btn-sm btn-teal"><i class="far fa-edit"></i></button></td>');
            });
          });
        },

        removeDisabledButtons = e => {

          let $tableId = $(e.target).closest('.wrapper-row-editor').find('table').attr('id'),
            $findButton = $(`#${$tableId}`).closest('.wrapper-row-editor').find('.removeColumns');

          if ($(`#${$tableId}`).find('td').hasClass('td-editor') == true) {

            $findButton.prop('disabled', false);
          } else {

            $findButton.prop('disabled', true);
          }

          if (!$(`#${$tableId}`).closest('.wrapper-row-editor').find('td.td-editor').hasClass('td-editor')) {

            $findButton.prop('disabled', true);
          }
        },

        editRowAndAddClassToTr = e => {

          let $closestTrTd = $(e.target).closest('.wrapper-row-editor tr').find('td'),
            $closestTrEdit = $(e.target).closest('.wrapper-row-editor tr').find(editRow),
            divWrapper = '<div class="d-flex justify-content-center div-to-remove"></div>',
            editButton = '<td class="text-center td-editor td-yes" style="border:none"><button class="btn btn-sm btn-danger deleteRow" style="cursor:pointer;"><i class="fas fa-trash-alt"></i></b></td>',
            saveButton = '<td class="text-center td-editor td-yes" style="border:none"><button class="btn btn-sm btn-primary saveRow" style="cursor:pointer;"><i class="fas fa-check"></i></button></td>';


          for (let i = 0; i < $(e.target).closest('.wrapper-row-editor').find('table thead th').length; i++) {

            $closestTrTd.eq(i).html(`<input type="text" class="val${i} form-control" value="${$closestTrTd.eq(i).text()}">`);
          }

          $closestTrEdit.after($(divWrapper).append(saveButton, editButton));

          $($(`#${$tableId}`)).on('click', '.deleteRow', () => {

            $($(`#${$tableId}`).closest('.wrapper-row-editor').find('.showForm, .closeByClick').removeClass('d-none'));
          });
        },

        clickBtnCBCaddDnone = e => {

          $(e.target).addClass('d-none');
          $showForm.addClass('d-none');
        },

        addDnoneByClickBtns = () => {

          $showForm.addClass('d-none');
          $closeByClick.addClass('d-none');
        },

        addColorClassAndPy = e => {

          let $closestTr = $(e.target).closest('tr');

          $closestTr.addClass('tr-color-selected');
          $closestTr.find('td').not('.td-editor').addClass('py-5');
        },

        addDisabledButtonsByEditBtn = e => {

          $(e.target).prop('disabled', true);
          $(e.target).closest('.wrapper-row-editor').find($removeColumns).prop('disabled', true);
        },

        saveRowAndRemovePy = e => {

          let $closestTr = $(e.target).closest('tr');

          for (let i = 0; i < $(e.target).closest('.wrapper-row-editor').find('table thead th').length; i++) {

            $tableData.cell($closestTr.find('td').eq(i)).data($closestTr.find('.val' + i).val());
          }

          $closestTr.find('td').removeClass('py-5');
        },

        removeDisabledColorAdnTdYes = e => {

          let $closestTr = $(e.target).closest('tr');

          $closestTr.find(editRow).prop('disabled', false);
          $closestTr.removeClass('tr-color-selected');
          $closestTr.find('.td-yes').remove();
          $tableData.draw(false);

          $(`#${$(this).closest('.wrapper-row-editor').find('table').attr('id')}`).closest('.wrapper-row-editor').find('.removeColumns').prop('disabled', false);
        },

        saveRowClickRemoveDiv = () => $('.div-to-remove').remove(),

        removeColorInTrAndDraw = e => {

          let $tableId = $(e.target).closest('.wrapper-row-editor').find('table').attr('id');

          $tableData.row($(`#${$tableId}`).find('tr.tr-color-selected')).remove().draw(false);

          if (!$(`#${$tableId} tr`).hasClass('td-editor')) {

            $(`#${$tableId}`).closest('.wrapper-row-editor').find($removeColumns).prop('disabled', false);
          } else {

            $(`#${$tableId}`).closest('.wrapper-row-editor').find($removeColumns).prop('disabled', true);
          }
        },

        removeSelectedButtonsFromRow = e => {

          let $tableId = $(e.target).closest('.wrapper-row-editor').find('table').attr('id');

          if (!$(`#${$tableId}`).hasClass('td-editor') === true) {

            $(e.target).closest('.wrapper-row-editor').find('.removeColumns').attr('disabled', true);
          }
          if ($(`#${$tableId}`).hasClass('td-editor') === false && $('#' + $tableId + ' tr').hasClass('tr-color-selected') === false) {

            $(`#${$tableId}`).find('.td-editor').remove();
            $(`#${$tableId}`).find('.tr-color-selected').remove();
            $tableData.draw(false);
          }
        },

        bindEvents = () => {

          $buttonWrapper.on('click', addNewColumn, addNewTr);
          $buttonWrapper.on('click', addNewColumn, removeDisabledButtons);
          $this.on('click', editRow, editRowAndAddClassToTr);
          $this.on('click', editRow, addColorClassAndPy);
          $this.on('click', editRow, addDisabledButtonsByEditBtn);
          $this.on('click', saveRow, saveRowAndRemovePy);
          $this.on('click', saveRow, removeDisabledColorAdnTdYes);
          $this.on('click', saveRow, saveRowClickRemoveDiv);
          $('.buttonYesNoWrapper').on('click', '.btnYes', removeColorInTrAndDraw);
          $buttonWrapper.on('click', '.removeColumns', removeSelectedButtonsFromRow);
          $showForm.on('click', '.btnYes, .button-x, .btnNo', addDnoneByClickBtns);
          $closeByClick.on('click', clickBtnCBCaddDnone);
        }

      bindEvents();

      if ($closeByClick.hasClass('d-none') === true) {

        $(document).keyup(e => {

          if (e.keyCode === 27) {

            $closeByClick.addClass('d-none');
            $showForm.addClass('d-none');
          }
        });
      }
    });
  };

  $('.buttonWrapper').on('click', '.addNewRows', e => {

    let $newRow = [];

    for (let i = 0; i < $(e.target).closest('.wrapper-row-editor').find('table thead th').length; i++) {

      $newRow.push($(e.target).val());
    }

    $('#' + $(e.target).closest('.wrapper-row-editor').find('table').attr('id')).DataTable().row.add($newRow).draw();
  });

})(jQuery);
