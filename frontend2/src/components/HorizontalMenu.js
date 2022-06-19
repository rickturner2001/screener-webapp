
export const HorizontalMenu = (props) =>{

    return(
        <ul className="menu menu-horizontal bg-base-100 rounded-box shadow-lg">
            {props.menuItems.menuText.map((text, index) =>{
                return (
                    <li key={index}>
                        <div className='flex flex-col'>
                            {props.menuItems.menuIcons[index]}
                            <p>{text}</p>
                        </div>
                    </li>
                )
            })}
        </ul>
    )
}

