
const states = ['notSelected', 'include', 'exclude']
let tagState = {}
let tagMapping = {}

async function main() {
    const tagsRaw = await fetch('/tags')
    const tags = await tagsRaw.json()

    // Add tags to form
    const tagTarget = document.querySelector('#tags')
    for (let i = 0; i < tags.length; i ++) {
        const tagTitle = tags[i]
        tagState[tagTitle] = 0
        tagTarget.appendChild(createTag(tagTitle))
    }

    // Load query parameter data
    const urlParams = new URLSearchParams(window.location.search);
    const loadedIncludes = urlParams.getAll('includes[]')
    const loadedExcludes = urlParams.getAll('excludes[]')
    const loadedLang = urlParams.get('ln')

    // Impute onto page
    for (let i = 0; i < loadedIncludes.length; i ++) {
        const tagTitle = loadedIncludes[i]
        if (tagTitle === '') continue
        tagState[tagTitle] = 1
        tagMapping[tagTitle].classList.remove(states[0])
        tagMapping[tagTitle].classList.add(states[1])
    }
    for (let i = 0; i < loadedExcludes.length; i ++) {
        const tagTitle = loadedExcludes[i]
        if (tagTitle === '') continue
        tagState[loadedExcludes[i]] = 2
        tagMapping[tagTitle].classList.remove(states[0])
        tagMapping[tagTitle].classList.add(states[2])
    }
    if (loadedLang) {
        document.querySelector(`#${loadedLang}`).checked = true
    }

    // Handle submit logic
    const submitBt = document.querySelector('#submit')
    const clearBt = document.querySelector('#clear')
    submitBt.addEventListener('click', () => handleSearch())
    clearBt.addEventListener('click', clearSearch)

    // Handle Pagination logic
    const page = urlParams.get('p')
    const paginationTarget = document.querySelector('#page-controls')
    if (!page || +page === 0) {
        createCurrentPage(0)
        createPaginationButtons(1)
        createPaginationButtons(2)
    } else if (+page === 1) {
        createPaginationButtons(+page - 1)
        createCurrentPage(1)
        createPaginationButtons(+page + 1)
        createPaginationButtons(+page + 2)

    } else {
        createPaginationButtons(+page - 2)
        createPaginationButtons(+page - 1)
        createCurrentPage(+page)
        createPaginationButtons(+page + 1)
        createPaginationButtons(+page + 2)
    }
}

function createTag(tagTitle) {
    // Create HTML object
    const element = document.createElement('button')
    element.textContent = tagTitle
    element.classList.add('tag')
    element.classList.add(states[tagState[tagTitle]])

    // Update state each time button is clicked
    element.addEventListener('click', () => {
        element.classList.remove(states[tagState[tagTitle]])
        if (tagState[tagTitle] === 2) {
            tagState[tagTitle] = 0
        } else {
            tagState[tagTitle] += 1
        }
        element.classList.add(states[tagState[tagTitle]])
    })

    // Add to tag mapping
    tagMapping[tagTitle] = element

    return element
}

function handleSearch(page) {
    // Gather all tags
    let includes = []
    let excludes = []
    for (const [tag, state] of Object.entries(tagState)) {
        if (state === 1) {
            includes.push(tag)
        } else if (state === 2) {
            excludes.push(tag)
        }
    }

    // Gather the original language
    let lang = '';
    const ko = document.querySelector('#ko').checked
    const ja = document.querySelector('#ja').checked
    if (ko ^ ja) { // Bitwise XOR
        if (ko) lang = 'ko'
        if (ja) lang = 'ja'
    }

    // Build Query Params
    const includesQuery = `&includes[]=${includes.join('&includes[]=')}`
    const excludesQuery = `&excludes[]=${excludes.join('&excludes[]=')}`
    const pageQuery = (page) ? page : ''

    window.location.href = `/?${includesQuery}${excludesQuery}&ln=${lang}&p=${pageQuery}`
}

function clearSearch() {
    // Clear languages
    document.querySelector('#ko').checked = false
    document.querySelector('#ja').checked = false

    // Clear Tags
    for (const [tag, curState] of Object.entries(tagState)) {
        tagMapping[tag].classList.remove(states[curState])
        tagMapping[tag].classList.add(states[0])
        tagState[tag] = 0;
    }
}

function createPaginationButtons(page) {
    const paginationTarget = document.querySelector('#page-controls')
    const button = document.createElement('button')
    button.addEventListener('click', () => {handleSearch(page)})
    button.textContent = page
    paginationTarget.appendChild(button)
}

function createCurrentPage(page) {
    const paginationTarget = document.querySelector('#page-controls')
    const form = document.createElement('form')
    const curPageElem = document.createElement('input')
    curPageElem.value = page
    form.addEventListener('submit', (e) => {
        e.preventDefault()
        const inputNum = +curPageElem.value
        if (inputNum) {
            handleSearch(inputNum)
        }
    })
    form.appendChild(curPageElem)
    paginationTarget.appendChild(form)
}

main()
