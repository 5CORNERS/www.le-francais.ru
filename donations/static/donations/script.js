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
    $('#whyItsImportant').popover({
        content: `Это для нас единственный источник средств для оплаты серверов, лицензий и многих других платных сервисов, которые используются в проекте и которые в большей своей части находятся за рубежом.<img class="server-map-image-link" alt='' src='${SERVERS_MAP_LINK}'>`,
        placement: 'top',
        trigger: 'focus',
        html: true,
        boundary: 'viewport'
    }).on('shown.bs.popover', function () {
        $('.pop-close').on('click', function () {
            $('#whyItsImportant').popover('hide')
        })
        $('.server-map-image-link').click(function () {
            $('#whyItsImportant').popover('hide')
            $('#serversMapImageModal').modal('show').one('hide.bs.modal', function () {
                // $('#whyItsImportant').popover('show')
            })
        })
    })
})
