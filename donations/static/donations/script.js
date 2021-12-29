$(document).ready(() => {
    let $typePills = $('#donationFormTypePills .nav-link')
    let $typeInput = $('#donationFormType')
    $typePills.click(e => {
        e.preventDefault()
        $typePills.toggleClass('active')
        $typeInput.val($(e.target).data('value'))
        console.log($(e.target).data('value'))
    })

    let $amountPills = $('#donationsFormAmountPills .nav-link')
    let $amountDummyInput = $('#donationsFormAmountPillsCustom')
    let $amountInput = $('#donationFormAmount')
    $amountPills.click(e => {
        e.preventDefault()
        let $this = $(e.currentTarget)
        $amountPills.removeClass('active')
        $this.addClass('active')
        if ($this.data('value')){
            $amountDummyInput.val('')
            $amountInput.val($this.data('value'))
            console.log($this.data('value'))
        }else{
            $amountInput.val($(e.target).val())
            console.log($(e.target).val())
        }
    })
    $amountDummyInput.focus(e => {
        $amountDummyInput.attr('placeholder', '')
    })
    $amountDummyInput.blur(e => {
        $amountDummyInput.attr('placeholder', 'Другая сумма')
    })
    $amountDummyInput.change(e => {
        $amountInput.val($(e.target).val())
        console.log($(e.target).val())
    })
})
