
const states = ['notSelected', 'include', 'exclude']
let tagState = {}

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
        if (tagState[tagTitle] == 2) {
            tagState[tagTitle] = 0
        } else {
            tagState[tagTitle] += 1
        }
        element.classList.add(states[tagState[tagTitle]])
        console.log(tagState)
    })

    return element
}

main()
